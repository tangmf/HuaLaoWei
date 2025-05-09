import httpx
import asyncio
import turfpy.measurement as measurement
from geojson import Point, Feature, FeatureCollection

class OSMGeospatialModule:
    async def get_poi_features(self, latitude: float, longitude: float):
        bbox = {
            "minLat": latitude - 0.01,
            "minLon": longitude - 0.01,
            "maxLat": latitude + 0.01,
            "maxLon": longitude + 0.01
        }

        groups = {
            "commercial": {"shop": True, "amenity": ["marketplace", "mall"]},
            "residential": {"landuse": "residential", "building": ["apartments", "residential"]},
            "facilities": {"amenity": ["school", "hospital"]},
            "recreation": {"leisure": "park", "tourism": True},
            "transit": {"highway": "bus_stop", "railway": ["station", "subway_entrance"], "public_transport": ["platform", "stop_position"]}
        }

        async def fetch_group(group_name, tags):
            query = f"""
[out:json][timeout:25];
(
    {"".join(
        f'node["{k}"="{v}"]({bbox["minLat"]},{bbox["minLon"]},{bbox["maxLat"]},{bbox["maxLon"]});' if not isinstance(v, list) 
        else "".join(f'node["{k}"="{vv}"]({bbox["minLat"]},{bbox["minLon"]},{bbox["maxLat"]},{bbox["maxLon"]});' for vv in v)
        for k, v in tags.items()
    )}
);
out center;
"""
            async with httpx.AsyncClient() as client:
                response = await client.post("https://overpass-api.de/api/interpreter", data=query)
                response.raise_for_status()
                data = response.json()
            return [{"lat": el["lat"], "lon": el["lon"]} for el in data.get("elements", [])]

        center = {"lat": latitude, "lon": longitude}
        tasks = [fetch_group(group, tags) for group, tags in groups.items()]
        results = await asyncio.gather(*tasks)

        features = {}
        for (group, pois) in zip(groups.keys(), results):
            features[f"density_{group}"] = len(pois)
            features[f"proximity_{group}"] = min(
                [measurement.distance(Point((p["lon"], p["lat"])), Point((center["lon"], center["lat"]))) for p in pois],
                default=None
            )

        return features
