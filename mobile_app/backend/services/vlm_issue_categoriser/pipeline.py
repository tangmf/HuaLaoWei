"""
pipeline.py

Main vlm issue categoriser pipeline entry point.

This script defines the VLMIssueCategoriserPipeline class for the HuaLaoWei mobile application, 
...

Authors: Jerick Cheong (Main Logic), Fleming Siow (Refactoring)
Date: 4th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import io
import logging

from typing import Optional, Tuple, List
from PIL import Image
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


class VLMIssueCategoriserPipeline:
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
    
    async def run(self, input) -> dict:
        # Extract user input
        input_text, input_images, input_coordinates = self._extract_input(input)

        # Validate images and load them if there is any
        images = self._validate_and_load_images(input_images or [])

        # LOCATION EXTRACTOR: Extract the coordinates from image metadata if possible
        latitude, longitude = self._extract_coordinates(images, input_coordinates)

        # GEOSPATIAL TAGGER: Retrives useful geospatial information tags based on the location
        tag_text = self._get_location_tags(latitude, longitude)
        full_text = input_text + tag_text

        # Prepare images for querying
        images = self._prepare_payload(images)

        # QUERY VLM: Predict issue category and severity based on any relevant text and images
        response = self._call_model_api(full_text, images)

        return self._finalise_response(response)

    def _extract_input(self, input):
        return (
            input.get("text") if isinstance(input, dict) else None,
            input.get("images") if isinstance(input, dict) else None,
            input.get("coordinates") if isinstance(input, dict) else None
        )

    async def _validate_and_load_images(self, files) -> List[Image.Image]:
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        images = []
        for file in files:
            if file.content_type in allowed_types:
                data = file.file.read()
                image = Image.open(io.BytesIO(data)).convert("RGB")
                images.append(image)
        return images

    async def _extract_coordinates(self, images, coordinates) -> Tuple[Optional[float], Optional[float]]:
        if coordinates:
            return coordinates.lat, coordinates.lon
        elif images:
            return self.location_extractor.extract_location(images[0])
        return None, None

    async def _get_location_tags(self, lat, lon) -> str:
        if lat is None or lon is None:
            return ""
        tags = self.geo_tagger.get_tags(lat, lon)
        nearby = ", ".join([f"{k}: {v}" for tag in tags["nearby"] for k, v in tag.items()])
        enclosing = ", ".join([f"{k}: {v}" for tag in tags["enclosing"] for k, v in tag.items()])
        return f"\n\nNearby location tags: {nearby}\n\nEnclosing location tags: {enclosing}"

    async def _prepare_payload(self, images: List[Image.Image]) -> Tuple[dict, List[tuple]]:
        image_buffers = []
        for idx, img in enumerate(images):
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            buf.seek(0)
            image_buffers.append(("files", (f"image{idx}.jpeg", buf, "image/jpeg")))
        return image_buffers

    async def _call_model_api(self, full_text: str, image_files: List[tuple]) -> dict:
        return await self.query_service.categorise(full_text, image_files)

    async def _finalise_response(self, response: dict) -> dict: 
        categories = response.get("categories", [])
        severity = response.get("severity")

        return {"categories": categories, "severity": severity}