"""
pipeline.py

ForecastIssueCountPipeline for municipal issue forecasting.

This pipeline coordinates fetching subzone data, external weather, air quality, POI,
socioeconomic, temporal features, assembles them, and runs model inference.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging

from modules.subzone import SubzoneService
from modules.open_meteo import OpenMeteoWeatherService
from modules.osm import OSMService
from modules.one_map import OneMapSocioeconomicService
from modules.temporal_features import TemporalFeaturesService
from modules.feature_engineering import FeatureEngineeringService
from modules.model_inference import ModelInferenceService

# --------------------------------------------------------
# Logger Configuration
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Forecast Pipeline
# --------------------------------------------------------

class ForecastIssueCountPipeline:
    """
    ForecastIssueCountPipeline manages the end-to-end forecasting
    of municipal issue counts for the next 7 days, for a specific subzone and issue type.
    """

    def __init__(self):
        logger.info("INITIALISING FORECAST PIPELINE")

        logger.info("LOADING MODULE | Subzone Service")
        self.subzone_service = SubzoneService()

        logger.info("LOADING MODULE | Weather and Air Forecast Service")
        self.weather_service = OpenMeteoWeatherService()

        logger.info("LOADING MODULE | OSM Geospatial Service")
        self.osm_service = OSMService()

        logger.info("LOADING MODULE | Socioeconomic Service via OneMap")
        self.socioeconomic_service = OneMapSocioeconomicService()

        logger.info("LOADING MODULE | Temporal Feature Generator")
        self.temporal_service = TemporalFeaturesService()

        logger.info("LOADING MODULE | Feature Engineering Assembler")
        self.feature_engineering = FeatureEngineeringService()

        logger.info("LOADING MODULE | Model Inference Service")
        self.model_inference = ModelInferenceService()

        logger.info("FORECAST PIPELINE INITIALISED")

    async def run(self, subzone_name: str, issue_type_name: str):
        """
        Run the forecast pipeline for a given subzone and issue type.

        Args:
            subzone_name (str): Subzone name.
            issue_type_name (str): Issue type name.

        Returns:
            dict: Forecasted issue counts for 7 days.
        """
        # Get Subzone Info
        latlon = await self.subzone_service.get_subzone_centroid(subzone_name)
        planning_area = await self.subzone_service.get_planning_area(subzone_name)
        if not latlon or not planning_area:
            raise ValueError("Subzone not found")

        latitude, longitude = latlon

        # Fetch Weather and Air Quality Forecast
        weather_air = await self.weather_service.get_weather_and_air_forecast(latitude, longitude)

        # Fetch OSM Geospatial Features
        poi_features = await self.osm_service.get_poi_features(latitude, longitude)

        # Fetch Socioeconomic Features
        socioeconomic_features = await self.socioeconomic_service.get_socioeconomic_features(planning_area)

        # Generate Temporal Features
        temporal_features = self.temporal_service.generate_temporal_features()

        # Assemble Feature Matrix
        feature_matrix = self.feature_engineering.prepare_forecast_features(
            weather_air, poi_features, socioeconomic_features, temporal_features
        )

        # Run Model Inference
        forecast = await self.model_inference.forecast_issue_counts(issue_type_name, feature_matrix)

        return {
            "subzone": subzone_name,
            "issueType": issue_type_name,
            "forecast": forecast
        }
