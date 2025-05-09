from fastapi import APIRouter, Request
from mobile_app.backend.models.vlm_issue_categoriser_input import VLMIssueCategoriserInput
from services.vlm_issue_categoriser.pipeline import VLMIssueCategoriserPipeline

router = APIRouter()
pipeline = VLMIssueCategoriserPipeline()

@router.post("/categorise")
async def infer_vlm_and_categorise_issues(input: VLMIssueCategoriserInput, request: Request):
    response = pipeline.run(input=input.dict())
    return {"response": response}
