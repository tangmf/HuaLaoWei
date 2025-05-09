from backend.data_stores.resources import Resources
from backend.crud import issues as crud_issues
from backend.models.posts import Post
from backend.models.issues import IssueReport, IssueFilter

async def fetch_issue_types_and_subtypes(resources: Resources):

    rows = await crud_issues.get_issue_type_and_subtype(resources)

    result = {}
    for row in rows:
        type_id = row["issue_type_id"]
        if type_id not in result:
            result[type_id] = {
                "issue_type_id": type_id,
                "name": row["type_name"],
                "description": row["type_description"],
                "subtypes": []
            }
        if row["issue_subtype_id"]:
            result[type_id]["subtypes"].append({
                "issue_subtype_id": row["issue_subtype_id"],
                "name": row["subtype_name"],
                "description": row["subtype_description"]
            })
            
    return list(result.values())


async def fetch_issues_nearby_for_forum_post(resources: Resources, lat: float, lon: float, radius: int = 100):

    rows = await crud_issues.get_issues_nearby(resources=resources, lat=lat, lon=lon, radius=radius)

    issues = {}
    for row in rows:
        issue_id = row["issue_id"]
        if issue_id not in issues:
            issues[issue_id] = {
                **{k: row[k] for k in Post.__fields__ if k not in {"comments"}},
                "comments": []
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


async def fetch_issue_reports(resources: Resources, filters: IssueFilter):

    rows = await crud_issues.get_issues(resources=resources, filters=filters)
            
    return list(issues.values())


async def submit_issue_report(resources: Resources, issue: IssueReport):

    rows = await crud_issues.get_issues_nearby(resources=resources, issues=issues)

    issues = {}
    for row in rows:
        issue_id = row["issue_id"]
        if issue_id not in issues:
            issues[issue_id] = {
                **{k: row[k] for k in Post.__fields__ if k not in {"comments"}},
                "comments": []
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

