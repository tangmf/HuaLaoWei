from fastapi import APIRouter, Request, Depends
from backend.models.chatbot import ChatbotInput
from backend.services.chatbot.service import ChatbotService
from backend.core.security import verify_token

router = APIRouter()

@router.post("/ask")
async def ask_chatbot(request: Request, input: ChatbotInput, user_id: int = Depends(verify_token), session_id: str = None):
    resources = request.app.state.resources
    chatbot_service = ChatbotService()
    response = chatbot_service.run(resources=resources, input=input.dict(), user_id=user_id, session_id=session_id)
    return {"response": response}
