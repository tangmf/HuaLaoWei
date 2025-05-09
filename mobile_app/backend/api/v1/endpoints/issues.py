from fastapi import APIRouter, Request
from mobile_app.backend.crud import issues as crud_issues
from mobile_app.backend.crud import authorities as crud_authorities
from mobile_app.backend.services.issues import helpers

router = APIRouter()

@router.get("/types")
async def get_issue_types_and_subtypes():
    rows = await crud_issues.fetch_issue_type_subtype_rows()
    return helpers.format_issue_types_and_subtypes(rows)

@router.get("/")
async def get_issues(lat: float, lon: float, request: Request, radius: int = 100):
    rows = await crud_issues.get_issues_nearby(lat, lon, radius)
    issues = {}

    for row in rows:
        issue_id = row["issue_id"]
        if issue_id not in issues:
            issues[issue_id] = {
                "issue_id": row["issue_id"],
                "user_id": row["user_id"],
                "issue_type_id": row["issue_type_id"],
                "issue_subcategory_id": row["issue_subcategory_id"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "address": row["address"],
                "location": row["location"],
                "description": row["description"],
                "severity": row["severity"],
                "status": row["status"],
                "datetime_reported": row["datetime_reported"],
                "datetime_acknowledged": row["datetime_acknowledged"],
                "datetime_closed": row["datetime_closed"],
                "datetime_updated": row["datetime_updated"],
                "agency_id": row["agency_id"],
                "town_council_id": row["town_council_id"],
                "subzone_id": row["subzone_id"],
                "planning_area_id": row["planning_area_id"],
                "is_public": row["is_public"],
                "post_id": row["post_id"],
                "created_at": row["created_at"],
                "comments": [],
                "comment_count": row["comment_count"],
                "post_likes": row["post_likes"],
            }
        if row["comment_id"]:
            issues[issue_id]["comments"].append({
                "comment_id": row["comment_id"],
                "parent_comment_id": row["parent_comment_id"],
                "content": row["comment_content"],
                "comment_created_at": row["comment_created_at"],
                "comment_likes": row["comment_likes"],
            })

    return list(issues.values())

@router.post("/")
async def create_issue(issue: dict, request: Request):
    issue["issue_types"] = [crud_issues.fetch_issue_type_id_from_name(i) for i in issue["issue_types"]]
    issue["issue_subtypes"] = [crud_issues.fetch_issue_subtype_id_from_name(i) for i in issue["issue_types"]]

    issue["agency"] = crud_authorities.fetch_agency_id_from_name(issue["agency"])
    issue["town_council"] = crud_authorities.fetch_town_council_id_from_name(issue["town_council"])

    new_issue = await crud_issues.create_issue(issue)
    return {"message": "Issue created successfully", "issue_id": new_issue["issue_id"]}
