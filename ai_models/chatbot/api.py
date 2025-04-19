# api.py

import os
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from app import ChatbotPipeline
import shutil
import uuid

# Optional override (you can also use ENV in Docker or FunctionGraph env vars)
os.environ.setdefault("ENV", "dev")

app = FastAPI()
pipeline = ChatbotPipeline()

class QueryInput(BaseModel):
    query: str

@app.post("/chat")
def handle_text(query: QueryInput):
    response = pipeline.run(input_text=query.query)
    return {"response": response}

@app.post("/voice")
def handle_voice(file: UploadFile = File(...)):
    temp_path = f"/tmp/{uuid.uuid4()}.wav"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    response = pipeline.run(input_audio_path=temp_path)
    return {"response": response}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Chatbot is running."}
