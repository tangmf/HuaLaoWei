from fastapi import APIRouter, Request, Depends
from mobile_app.backend.models.chatbot_input import ChatbotInput
from mobile_app.backend.services.chatbot.pipeline import ChatbotPipeline
from mobile_app.backend.core.security import verify_token

router = APIRouter()
pipeline = ChatbotPipeline()

@router.post("/ask")
async def ask_chatbot(input: ChatbotInput, request: Request, user_id: int = Depends(verify_token)):
    response = pipeline.run(input=input.dict(), user_id=user_id)
    return {"response": response}
