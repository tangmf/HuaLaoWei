from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from backend.services.issues import service
from backend.models.issues import IssueReport, IssueFilter, Proximity, Location
from backend.services.vlm_issue_categoriser.service import VLMIssueCategoriserService
from backend.services.stfm_issue_count.service import STFMIssueCountService

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


@router.post("/categorise")
async def infer_vlm_and_categorise_issues(
    request: Request,
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    images: Optional[List[UploadFile]] = File(None)
):
    """
    Example curl request:

    curl -X POST "http://localhost:XXXX/categorise" \
    -F "description=Overflowing trash bin at junction" \
    -F "latitude=1.3521" \
    -F "longitude=103.8198" \
    -F "address=Block 123, Singapore" \
    -F "images=@/path/to/photo1.jpg" \
    -F "images=@/path/to/photo2.jpg"
    """
    location = Location(latitude=latitude, longitude=longitude, address=address)

    input_payload = {
        "description": description,
        "location": location,
        "images": images  # Optional: Pass to service if given
    }

    resources = request.app.state.resources
    vlm_issue_categoriser_service = VLMIssueCategoriserService()
    response = vlm_issue_categoriser_service.run(resources=resources, input=input_payload)

    return JSONResponse(content={"response": response})


@router.post("/forecast")
async def infer_vlm_and_categorise_issues(
    request: Request, 
    subzone_name: str = Query(...), 
    issue_type: str = Query(...)
):
    resources = request.app.state.resources
    sftm_issue_count_service = STFMIssueCountService()
    response = sftm_issue_count_service.run(resources=resources, subzone_name=subzone_name, issue_type=issue_type)
    return {"response": response}
