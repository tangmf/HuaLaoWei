from fastapi import APIRouter, Query
from dashboard.backend.crud import subzone

router = APIRouter(prefix="/api/subzone", tags=["Subzone"])

@router.get("/planning-area")
async def get_planning_area(subzoneName: str = Query(..., alias="subzoneName")):
    return await subzone.get_planning_area(subzoneName)
