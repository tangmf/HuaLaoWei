from fastapi import APIRouter, Query
from typing import Optional
from dashboard.backend.crud import issues

router = APIRouter(prefix="/api/issues", tags=["Issues"])

@router.get("/open")
async def get_open_issues(
    subzoneName: Optional[str] = None,
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None,
    types: Optional[str] = None,
    subtypes: Optional[str] = None,
    severity: Optional[str] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 10000
):
    params = {"subzoneName": subzoneName, "from": from_, "to": to, "types": types, "subtypes": subtypes, "severity": severity, "page": page, "limit": limit}
    return await issues.get_open_issues(params)

@router.get("/resolved")
async def get_resolved_issues(
    subzoneName: Optional[str] = None,
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None,
    types: Optional[str] = None,
    subtypes: Optional[str] = None,
    severity: Optional[str] = None,
    page: Optional[int] = 1,
    limit: Optional[int] = 10000
):
    params = {"subzoneName": subzoneName, "from": from_, "to": to, "types": types, "subtypes": subtypes, "severity": severity, "page": page, "limit": limit}
    return await issues.get_resolved_issues(params)

@router.get("/daily-count")
async def get_daily_count(subzoneName: Optional[str] = None, issueTypeName: Optional[str] = None):
    return await issues.get_daily_count(subzoneName, issueTypeName)
