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

from typing import Optional, Tuple, List
from PIL import Image

from mobile_app.backend.data_stores.resources import Resources
from modules.extract_location import GPSExtractor
from modules.geo_tagger import GeoTagger
from modules.query import QueryVLMIssueCategoriser

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
    
    async def run(self, resources: Resources, input: dict) -> dict:
         # Extracts the input, text and location (lat, lng) are a must, while images are optional
        input_text = input.get("text") if isinstance(input, dict) else None
        input_images = input.get("images") if isinstance(input, dict) else None
        input_coordinates = input.get("coordinates") if isinstance(input, dict) else None

        # Validate and load the images if any
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        images = []
        if input_images:
            for file in input_images:
                if file.content_type in allowed_types:
                    data = file.file.read()
                    image = Image.open(io.BytesIO(data)).convert("RGB")
                    images.append(image)

        # --------------------------------------------------------
        # LOCATION EXTRACTOR: If for some reason, location is not provided, extract the coordinates from image metadata
        # --------------------------------------------------------
        if input_coordinates:
            latitude, longitude = input_coordinates.lat, input_coordinates.lon
        elif images:
            latitude, longitude = self.location_extractor.extract_location(images[0])
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

        full_text = input_text + tag_text

        # --------------------------------------------------------
        # VLM QUERY: Performs categorisation of issue subtype and severity, as well as title generation
        # --------------------------------------------------------
        image_buffers = []
        for idx, img in enumerate(images):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            buf.seek(0)
            image_buffers.append(("files", (f"image{idx}.jpeg", buf, "image/jpeg")))

        response = await self.query_service.categorise(full_text, image_buffers)

        return self._finalise_response(response)

    async def _finalise_response(self, response: dict) -> dict: 
        categories = response.get("categories", [])
        severity = response.get("severity")

        return {"categories": categories, "severity": severity}