from backend.crud import regions as crud_regions
from backend.data_stores.resources import Resources

class RegionInfoModule:
    async def fetch_subzone_centroid(self, resources: Resources, subzone_name: str):
        return await crud_regions.get_subzone_centroid(resources=resources, params={"subzone_name": subzone_name})

    async def fetch_planning_area_info_from_subzone(self, resources: Resources, subzone_name: str):
        return await crud_regions.get_planning_area_info_from_subzone(resources=resources, params={"subzone_name": subzone_name})
