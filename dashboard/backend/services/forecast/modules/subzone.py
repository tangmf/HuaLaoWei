from dashboard.backend.crud import subzone as crud_subzone

class SubzoneService:
    async def get_subzone_centroid(self, subzone_name: str):
        return await crud_subzone.fetch_subzone_centroid(subzone_name)

    async def get_planning_area(self, subzone_name: str):
        return await crud_subzone.fetch_planning_area_by_subzone(subzone_name)
