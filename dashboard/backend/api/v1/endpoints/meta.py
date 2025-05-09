from fastapi import APIRouter
from dashboard.backend.crud import meta

router = APIRouter(prefix="/api/meta", tags=["Meta"])

@router.get("/issue-types")
async def get_issue_types():
    return await meta.get_issue_types()

@router.get("/agencies")
async def get_agencies():
    return await meta.get_agencies()

@router.get("/town-councils")
async def get_town_councils():
    return await meta.get_town_councils()
