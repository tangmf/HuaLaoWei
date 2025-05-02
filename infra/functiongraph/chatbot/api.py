from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from app import ChatbotPipeline
from dotenv import load_dotenv
from typing import Optional
from fastapi import Form
import shutil
import uuid

load_dotenv()

app = FastAPI()
pipeline = ChatbotPipeline()

class QueryInput(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[int] = None

@app.post("/chat")
def handle_text(query: QueryInput):
    response = pipeline.run(
        input_text=query.query, 
        session_id=query.session_id, 
        user_id=query.user_id
    )
    return {"response": response}

@app.post("/voice")
def handle_voice(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None)
):
    temp_path = f"/tmp/{uuid.uuid4()}.wav"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    response = pipeline.run(
        input_audio_path=temp_path,
        session_id=session_id,
        user_id=user_id
    )
    return {"response": response}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Chatbot is running."}
