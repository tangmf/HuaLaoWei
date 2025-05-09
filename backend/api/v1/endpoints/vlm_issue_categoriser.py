from fastapi import APIRouter, Request
from mobile_app.backend.models.vlm_issue_categoriser import VLMIssueCategoriserInput
from mobile_app.backend.services.vlm_issue_categoriser.service import VLMIssueCategoriserService

router = APIRouter()

@router.post("/categorise")
async def infer_vlm_and_categorise_issues(request: Request, input: VLMIssueCategoriserInput):
    resources = request.app.state.resources
    vlm_issue_categoriser_service = VLMIssueCategoriserService()
    response = vlm_issue_categoriser_service.run(resources=resources, input=input.dict())
    return {"response": response}
