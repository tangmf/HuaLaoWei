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

from backend.data_stores.resources import Resources
from backend.services.stfm_issue_count.modules.region import RegionInfoModule
from backend.services.stfm_issue_count.modules.weather import OpenMeteoWeatherModule
from backend.services.stfm_issue_count.modules.geospatial import OSMGeospatialModule
from backend.services.stfm_issue_count.modules.socioeconomic import OneMapAPISocioeconomicModule
from backend.services.stfm_issue_count.modules.temporal import TemporalGenerationModule
from backend.services.stfm_issue_count.modules.matrix import FeatureMatrixModule
from backend.services.stfm_issue_count.modules.forecaster import ModelForecaster

# --------------------------------------------------------
# Logger Configuration
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Spatio-Temporal Forecasting Model Issue Count Service
# --------------------------------------------------------

class STFMIssueCountService:
    """
    STFMIssueCountService manages the end-to-end forecasting
    of municipal issue counts for the next 7 days, for a specific subzone and issue type.
    """

    def __init__(self):
        logger.info("INITIALISING FORECAST PIPELINE")

        logger.info("LOADING MODULE | Region Information Retrieval")
        self.region_retrieval = RegionInfoModule()

        logger.info("LOADING MODULE | Weather and Air Forecast Service")
        self.weather_module = OpenMeteoWeatherModule()

        logger.info("LOADING MODULE | OSM Geospatial Service")
        self.geospatial_module = OSMGeospatialModule()

        logger.info("LOADING MODULE | Socioeconomic Service via OneMap")
        self.socioeconomic_module = OneMapAPISocioeconomicModule()

        logger.info("LOADING MODULE | Temporal Feature Generator")
        self.temporal_module = TemporalGenerationModule()

        logger.info("LOADING MODULE | Feature Engineering Assembler")
        self.feature_engineering = FeatureMatrixModule()

        logger.info("LOADING MODULE | Model Inference Service")
        self.model_inference = ModelForecaster()

        logger.info("FORECAST PIPELINE INITIALISED")

    async def run(self, resources: Resources, subzone_name: str, issue_type: str):
        """
        Run the forecast pipeline for a given subzone and issue type.

        Args:
            subzone_name (str): Subzone name.
            issue_type (str): Issue type name.

        Returns:
            dict: Forecasted issue counts for 7 days.
        """
        # --------------------------------------------------------
        # REGION INFORMATION: Performing analysis and forecasting on a planning area & subzone level
        # --------------------------------------------------------
        location = await self.region_retrieval.fetch_subzone_centroid(subzone_name)
        latitude, longitude = (location["latitude"], location["longitude"]) if location else (None, None)

        planning_area_info = await self.region_retrieval.fetch_planning_area_info_from_subzone(subzone_name)
        planning_area_name = planning_area_info["planning_area_name"]
        
        if not location or not planning_area_name:
            raise ValueError("Subzone not found")

        # --------------------------------------------------------
        # FETCHING WEATHER & AIR QUALITY DATA: Retrieve relevant weather and air quality data from Open-Meteo based on location
        # --------------------------------------------------------
        weather_air = await self.weather_module.get_weather_and_air_forecast(latitude, longitude)

        # --------------------------------------------------------
        # CONSTRUCTING GEOSPATIAL FEATURES: Engineer geospatial features based on the proximity and density of POIs to the location using OSM
        # --------------------------------------------------------
        poi_features = await self.geospatial_module.get_poi_features(latitude, longitude)

        # --------------------------------------------------------
        # FETCHING SOCIOECONOMIC DATA: Accessing socioeconomic data based on the location's planning area and subzone, with OneMap API
        # --------------------------------------------------------
        socioeconomic_features = await self.socioeconomic_module.get_socioeconomic_features(planning_area_name)

        # --------------------------------------------------------
        # GENERATING TEMPORAL FEATURES: Lessen the effects of seasonality, and instead focus on more day-to-day driven features
        # --------------------------------------------------------
        temporal_features = self.temporal_module.generate_temporal_features()

        # --------------------------------------------------------
        # ISSUE COUNT FORECAST: Assembles the feature matrix to forecast a window period of the next 7 days (inclusive of Today) based on past 14 days
        # --------------------------------------------------------
        feature_matrix = self.feature_engineering.prepare_forecast_features(
            weather_air, poi_features, socioeconomic_features, temporal_features
        )
        forecast = await self.model_inference.forecast_issue_counts(issue_type, feature_matrix)

        return {
            "subzone": subzone_name,
            "issue_type": issue_type,
            "forecast": forecast
        }
