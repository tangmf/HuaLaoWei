from fastapi import APIRouter, Request, Depends, Query
from typing import Optional
from mobile_app.backend.services.issues import service
from mobile_app.backend.models.issues import IssueReport, IssueFilter, Proximity

router = APIRouter()

@router.get("/categories")
async def get_issue_categories(request: Request):
    resources = request.app.state.resources
    return service.fetch_issue_types_and_subtypes(resources)

@router.get("/nearby")
async def get_issues_nearby_for_forum_post(request: Request, lat: float, lon: float, radius: int = 100):
    resources = request.app.state.resources
    return service.fetch_issues_nearby_for_forum_post(resources=resources, lat=lat, lon=lon, radius=radius)

@router.get("/")
async def get_issue_reports(
        request: Request, 
        from_: Optional[str] = Query(None, alias="from"),
        to: Optional[str] = None,
        types: Optional[str] = None,
        subtypes: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        subzone_name: Optional[str] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = 10000,
        proximity: Optional[Proximity] = Depends()
    ):

    filters = IssueFilter(
        from_=from_,
        to=to,
        types=types,
        subtypes=subtypes,
        severity=severity,
        status=status,
        subzone_name=subzone_name,
        page=page,
        limit=limit,
        proximity=proximity
    )

    resources = request.app.state.resources
    return service.fetch_issue_reports(resources=resources, filters=filters)

@router.post("/")
async def create_issue_report(request: Request, issue: IssueReport):
    resources = request.app.state.resources
    inserted_issue = await service.submit_issue_report(resources=resources, issue=issue)
    return {"message": "Issue created successfully", "issue_id": inserted_issue["issue_id"]}
