"""
service.py

Main vlm issue categoriser service entry point.

This script defines the VLMIssueCategoriserService class for the HuaLaoWei mobile application, 
...

Authors: Jerick Cheong (Original Logic), Fleming Siow (Refactor)
Date: 4th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import io
import logging

from fastapi import UploadFile
from typing import Optional, List
from PIL import Image

from backend.data_stores.resources import Resources
from backend.models.issues import Location
from backend.services.vlm_issue_categoriser.modules.extract_location import GPSExtractor
from backend.services.vlm_issue_categoriser.modules.geo_tagger import GeoTagger
from backend.services.vlm_issue_categoriser.modules.query import QueryVLMIssueCategoriser

# --------------------------------------------------------
# Logger Configuration
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# VLM Issue Categoriser Service
# --------------------------------------------------------

class VLMIssueCategoriserService:
    def __init__(self):
        logger.info("INITIALISING VLM ISSUE CATEGORISER PIPELINE\n")

        logger.info("LOADING MODULE | Location Extractor...")
        self.location_extractor = GPSExtractor()

        logger.info("LOADING MODULE | Geolocation Tagger...")
        self.geo_tagger = GeoTagger()

        logger.info("LOADING MODULE | Model Query Engine...")
        self.query_service = QueryVLMIssueCategoriser()
        
    async def setup(self):
        await self.query_service.load_context_data()
        await self.query_service.create_prompt()
    
    async def run(self, resources: Resources, description: str, location: Optional[Location] = None, images: Optional[List[UploadFile]] = None) -> dict:

        # Validate and load the images if any
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        if images:
            for i, file in enumerate(images):
                if file.content_type in allowed_types:
                    data = file.file.read()
                    image = Image.open(io.BytesIO(data)).convert("RGB")
                    images[i] = image
                    images.append(image)

        # --------------------------------------------------------
        # LOCATION EXTRACTOR: If for some reason, location is not provided, extract the location information from image metadata
        # --------------------------------------------------------
        if location:
            latitude, longitude, address = location.latitude, location.longitude, location.address
        elif images:
            latitude, longitude = self.location_extractor.extract_location(images[0])
            # TODO: Add logic to reverse geocode the address from the latitude and longitude
        else:
            latitude, longitude = None, None

        # --------------------------------------------------------
        # GEOSPATIAL TAGGER: Retrives useful geospatial information tags based on the location
        # --------------------------------------------------------
        if latitude is not None and longitude is not None:
            tags = self.geo_tagger.get_tags(latitude, longitude)
            nearby = ", ".join([f"{k}: {v}" for tag in tags["nearby"] for k, v in tag.items()])
            enclosing = ", ".join([f"{k}: {v}" for tag in tags["enclosing"] for k, v in tag.items()])
            tag_text = f"\n\nNearby location tags: {nearby}\n\nEnclosing location tags: {enclosing}"
        else:
            tag_text = ""

        full_text = description + tag_text

        # --------------------------------------------------------
        # VLM QUERY: Performs categorisation of issue subtype and severity, as well as title generation
        # --------------------------------------------------------
        image_buffers = []
        for idx, img in enumerate(images):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            buf.seek(0)
            image_buffers.append(("files", (f"image{idx}.jpeg", buf, "image/jpeg")))

        response = await self.query_service.categorise(text=full_text, location=location, images=image_buffers)

        return self._finalise_response(response)

    async def _finalise_response(self, response: dict) -> dict: 
        categories = response.get("categories", [])
        severity = response.get("severity")

        return {"categories": categories, "severity": severity}