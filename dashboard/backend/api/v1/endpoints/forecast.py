from fastapi import APIRouter, Query
from dashboard.backend.services.forecast.pipeline import ForecastIssueCountPipeline

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])

@router.get("/issues")
async def forecast_issues(subzoneName: str = Query(...), issueTypeName: str = Query(...)):
    pipeline = ForecastIssueCountPipeline()
    return await pipeline.run(subzone_name=subzoneName, issue_type_name=issueTypeName)
