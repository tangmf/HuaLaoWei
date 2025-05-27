from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from typing import List, Optional
from backend.services.chatbot.service import ChatbotService
from backend.core.security import verify_token

router = APIRouter()

@router.post("/text")
async def chat_with_text(
    request: Request, 
    text: str = Form(...),
    user_id: int = Form(Depends(verify_token)),
    session_id: str = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    resources = request.app.state.resources
    chatbot_service = ChatbotService()
    response = chatbot_service.run(resources=resources, text=text, user_id=user_id, session_id=session_id, files=files)
    return {"response": response}


@router.post("/audio")
async def chat_with_audio(
    request: Request, 
    audio: UploadFile = File(...),
    user_id: int = Form(Depends(verify_token)),
    session_id: str = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    resources = request.app.state.resources
    chatbot_service = ChatbotService()
    response = chatbot_service.run(resources=resources, audio=audio, user_id=user_id, session_id=session_id, files=files)
    return {"response": response}

