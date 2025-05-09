"""
query.py

Handles communication with the VLM Issue Categoriser
for issue categorising (issue type & severity) based on image and text input.

Authors: Jerick Cheong (Main Logic), Fleming Siow (Refactoring)
Date: 4th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import httpx
import json
import textwrap
from typing import Tuple, List, Optional
from config.config import config
from mobile_app.backend.crud import issues as crud_issues
from mobile_app.backend.models.location import Location 
# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Query VLM Issue Categoriser 
# --------------------------------------------------------

class QueryVLMIssueCategoriser:
    """
    QueryVLMIssueCategoriser sends image and text data to the 
    VLM API and returns the categorised response.
    """

    def __init__(self):
        self.env = config.env

        try:
            self.vlm_url = config.ai_models.vlm_issue_categoriser.url
        except AttributeError:
            raise ValueError("VLM Issue Categoriser url missing in config")

        logger.info(f"Loading VLM Issue Categoriser from: {self.vlm_url}")

    async def create_prompt(self):
        """
        Builds the base system prompt using preloaded data.
        """
        if not hasattr(self, 'categories') or not hasattr(self, 'agencies') or not hasattr(self, 'town_councils'):
            raise ValueError("Static data not loaded. Please call load_context_data() first.")

        categories_text = "\n".join(f"- {entry}" for entry in self.categories)
        agencies_text = "\n".join(f"- {entry}" for entry in self.agencies)
        town_council_text = "\n".join(f"- {entry}" for entry in self.town_councils)

        self.base_prompt_content = textwrap.dedent(f"""
            You are an expert in municipal services issues for Singapore.

            Your task is to carefully analyse the provided input, which may include:
            - A description of the issue.
            - Latitude and longitude of the location.
            - One or more images of the issue.

            After analysing, you must perform four sub-tasks:

            1. **Categories**:
            - Categorise the issue into one or more predefined categories.
            - Use only the exact provided category names (case sensitive).
            - Do not invent new categories.

            2. **Severity**:
            - Assess the severity of the issue as one of: Low, Medium, High.
            - Follow these guidelines:
                - Low: Minor inconvenience or cosmetic issue (e.g., dirty floor, faded paint).
                - Medium: Noticeable impact needing attention but not urgent (e.g., pothole, broken railing).
                - High: Critical issue requiring urgent action, public danger (e.g., exposed electrical wiring, large sinkhole).

            3. **Authority**:
            - Select the most appropriate authority responsible for handling the issue.
            - Choose either an Agency or a Town Council, not both.
            - Guidelines:
                - If the issue occurs near HDB residential blocks, playgrounds, common corridors, or neighbourhood surroundings, prefer Town Councils.
                - If the issue occurs in parks, public transport facilities, roads, expressways, rivers, public beaches, or national infrastructure, prefer Agencies.

            4. **Title**:
            - Generate a short, clear, and descriptive title between 5 to 12 words.
            - Title must be suitable for a forum post headline.
            - Include the location (block number, park name, road name) in the title only if it improves clarity.
            - Prioritise clarity and precision. Do not be overly creative.

            You must respond strictly in the following JSON format:
            {{
                "title": "string",
                "categories": ["list of selected categories as strings"],
                "severity": "Low" or "Medium" or "High",
                "authority": "Name of Agency or Town Council as string"
            }}

            Predefined Categories:
            {categories_text}

            Predefined Agencies:
            {agencies_text}

            Predefined Town Councils:
            {town_council_text}

            ----------------------------------------------------------
            Here are a few examples to guide you:

            **Example 1:**
            Input description: "There is a cracked and uneven floor at the corridor near Block 20, it is very dangerous for elderly."
            Location: 20 Jln Membina, Singapore 164020 (Latitude: 1.2855982, Longitude: 103.8257872)
            Image: Attached (shows cracked floor tiles).

            Output:
            {{
                "title": "Cracked Floor at Corridor of Block 20",
                "categories": ["Common area maintenance"],
                "severity": "Medium",
                "authority": "Tanjong Pagar Town Council"
            }}

            **Example 2:**
            Input description: "Tree branch fell onto the footpath near Bishan Park entrance. Blocking the way."
            Location: 1380 Ang Mo Kio Ave 1, Singapore 569930 (Latitude: 1.3642698, Longitude: 103.8435411)
            Image: Attached (shows fallen tree branch).

            Output:
            {{
                "title": "Fallen Tree Branch Blocking Footpath Near Bishan Park",
                "categories": ["Fallen trees or tree branches"],
                "severity": "High",
                "authority": "National Parks Board (NParks)"
            }}

            **Example 3:**
            Input description: "The traffic light at junction of Clementi Ave 2 and Commonwealth Ave West is not working properly."
            Location: Clementi Ave 2 (Latitude: 1.311955, Longitude: 103.767772)
            Image: Attached (shows faulty traffic lights).

            Output:
            {{
                "title": "Faulty Traffic Light at Clementi Ave 2 Junction",
                "categories": ["Faulty streetlights"],
                "severity": "High",
                "authority": "Land Transport Authority (LTA)"
            }}
            ----------------------------------------------------------

            Important Notes:
            - Always match category and authority names exactly.
            - Select the most logical and relevant authority based on the context.
            - Do not leave any fields blank.
            - If the images are unclear or missing, rely on the text description more.
        """)

    async def categorise(
        self,
        text: str,
        location: Location,
        images: Optional[List[Tuple[str, Tuple[str, bytes, str]]]] = None,
    ) -> dict:
        try:
            user_content = [{"type": "text", "text": text}, {"type": "text", "text": f"{location.address} (Latitude: {location.latitude}, Longitude: {location.longitude})"}]
            for _ in images:
                user_content.append({"type": "image"})

            messages = [
                {"role": "system", "content": self.base_prompt_content},
                {"role": "user", "content": user_content}
            ]

            # Build the data dictionary with everything stringified
            data = {
                "messages": json.dumps(messages),
                "classes": json.dumps(self.categories)
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.vlm_url, data=data, files=images)
                response.raise_for_status()
                raw_response = response.json()

                # Validate and fallback
                validated_response = await self._validate_response(raw_response)
                return validated_response
            
        except httpx.RequestError as e:
            logger.error(f"Failed to query VLM Issue Categoriser: {e}")
            raise

    async def load_context_data(self):
        """
        Preloads issue categories, agencies, and town councils into memory.
        This should be called once at app startup.
        """
        # Load categories
        issue_subtypes = await crud_issues.fetch_issue_subtype()
        self.categories = [
            f"{subtype['name']}: {subtype.get('description', 'No description provided')}"
            for subtype in issue_subtypes
        ]
        self.category_names = [subtype['name'] for subtype in issue_subtypes]  # pure names, no description

        # Load agencies
        agencies = await crud_issues.fetch_agencies()
        self.agencies = [
            f"{agency['name']}: {agency.get('description', 'No description provided')}"
            for agency in agencies
        ]
        self.agency_names = [agency['name'] for agency in agencies]

        # Load town councils
        town_councils = await crud_issues.fetch_town_councils()
        self.town_councils = [
            f"{council['name']}: {council.get('description', 'No description provided')}"
            for council in town_councils
        ]
        self.town_council_names = [council['name'] for council in town_councils]

        logger.info("Static data loaded successfully: Categories, Agencies, Town Councils.")

    async def _validate_response(self, response: dict) -> dict:
        """
        Validates the VLM response and applies fallback if necessary.
        """
        fallback_response = {
            "title": "Uncategorised Municipal Issue",
            "categories": ["Miscellaneous"],
            "severity": "Medium",
            "authority": "Unassigned"
        }

        try:
            if not isinstance(response, dict):
                raise ValueError("Response is not a dictionary")

            title = response.get("title")
            categories = response.get("categories")
            severity = response.get("severity")
            authority = response.get("authority")

            if not title or not isinstance(title, str):
                raise ValueError("Missing or invalid title")

            if not categories or not isinstance(categories, list) or not all(isinstance(c, str) for c in categories):
                raise ValueError("Missing or invalid categories")

            if severity not in ["Low", "Medium", "High"]:
                raise ValueError("Invalid severity")

            if not authority or not isinstance(authority, str):
                raise ValueError("Missing or invalid authority")

            return response 

        except Exception as e:
            logger.warning(f"Invalid VLM response detected: {e}. Using fallback response.")
            return fallback_response

