"""
geo_tagger.py

--

Author(s): Jerick Cheong (Original Logic), Fleming Siow (Refactor)
Date: 4th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import requests
import logging
from typing import List, Dict

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------------
# GeoTagger Class
# --------------------------------------------------------

class GeoTagger:
    """
    GeoTagger queries the Overpass API to retrieve OSM tags near a given coordinate.
    """

    def __init__(self, overpass_url: str = "https://overpass-api.de/api/interpreter"):
        self.RELEVANT_KEYS = {
            'name', 'place', 'amenity', 'landuse', 'leisure', 'building',
            'highway', 'natural', 'shop', 'tourism', 'man_made', 'railway'
        }
        
        self.overpass_url = overpass_url

    def get_tags(self, lat: float, lon: float, radius: int = 15, filter: bool = True) -> Dict[str, List[dict]]:
        tags = {"nearby": [], "enclosing": []}

        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            logger.warning("Invalid latitude or longitude values.")
            return tags

        lat_min = lat - 0.0015
        lat_max = lat + 0.0015
        lon_min = lon - 0.0015
        lon_max = lon + 0.0015
        bbox = f"{lat_min},{lon_min},{lat_max},{lon_max}"

        nearby_query = f"""
        [timeout:10][out:json];
        (
          node(around:{radius},{lat},{lon});
          way(around:{radius},{lat},{lon});
        );
        out tags geom({bbox});
        relation(around:{radius},{lat},{lon});
        out geom({bbox});
        """

        enclosing_query = f"""
        [timeout:10][out:json];
        is_in({lat},{lon})->.a;
        way(pivot.a);
        out tags bb;
        out ids geom({bbox});
        relation(pivot.a);
        out tags bb;
        """

        try:
            nearby_data = self._run_query(nearby_query)
            enclosing_data = self._run_query(enclosing_query)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying Overpass API: {e}")
            return tags

        for element in nearby_data.get("elements", []):
            if "tags" in element:
                tags["nearby"].append(element["tags"])

        for element in enclosing_data.get("elements", []):
            if "tags" in element:
                tags["enclosing"].append(element["tags"])

        if filter:
            tags["nearby"] = self._filter_tags(tags["nearby"])
            tags["enclosing"] = self._filter_tags(tags["enclosing"])

        return tags

    def _run_query(self, query: str) -> dict:
        response = requests.post(self.overpass_url, data={"data": query})
        response.raise_for_status()
        return response.json()

    def _filter_tags(self, tags: List[dict]) -> List[dict]:
        return [
            filtered_tag
            for tag in tags
            if (filtered_tag := {k: v for k, v in tag.items() if k in self.RELEVANT_KEYS})
        ]