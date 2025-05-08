"""
app.py

FastAPI server for to host HuaLaoWei chatbot's speech transcription, translation, embedding, and reranking services.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

from typing import List
import io
import httpx
import logging
import torch
import torchaudio
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    WhisperProcessor,
    WhisperForConditionalGeneration,
    pipeline
)
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, CrossEncoder

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Model Loading
# --------------------------------------------------------

device = "cuda" if torch.cuda.is_available() else "cpu"

def load_whisper_model():
    processor = WhisperProcessor.from_pretrained("models/whisper_tiny", task="transcribe", local_files_only=True)
    model = WhisperForConditionalGeneration.from_pretrained("models/whisper_tiny", local_files_only=True)
    model.generation_config.forced_decoder_ids = None
    model.to(device)
    return processor, model

def load_nllb_model():
    tokenizer = AutoTokenizer.from_pretrained("models/nllb_model", local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained("models/nllb_model", local_files_only=True)
    model.to(device)
    translator = pipeline("translation", model=model, tokenizer=tokenizer)
    return translator

def load_sentence_embedder():
    return SentenceTransformer("models/sentence_model")

def load_flash_reranker():
    return CrossEncoder("models/flash_reranker")

whisper_processor, whisper_model = load_whisper_model()
nllb_translator = load_nllb_model()
sentence_embedder = load_sentence_embedder()
flash_reranker = load_flash_reranker()

# --------------------------------------------------------
# FastAPI Setup
# --------------------------------------------------------

app = FastAPI()

# --------------------------------------------------------
# Request Models
# --------------------------------------------------------

class TextRequest(BaseModel):
    text: str

class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class Document(BaseModel):
    id: str
    score: float
    combined_text: str

class BatchTextRequest(BaseModel):
    text: str
    documents: List[Document]

# --------------------------------------------------------
# API Endpoints
# --------------------------------------------------------

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe an uploaded audio file using Whisper model.

    Args:
        file (UploadFile): Uploaded audio file (e.g., WAV format).

    Returns:
        dict: Transcribed text.
    """
    audio_bytes = await file.read()
    waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))

    inputs = whisper_processor(waveform.squeeze(), sampling_rate=sample_rate, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    predicted_ids = whisper_model.generate(**inputs)
    transcription = whisper_processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

    return {"transcription": transcription}

@app.post("/translate")
async def translate_text(req: TranslateRequest):
    """
    Translate input text using NLLB model.

    Args:
        req (TranslateRequest): Request containing text and language codes.

    Returns:
        dict: Translated text.
    """
    translation = nllb_translator(
        req.text,
        src_lang=req.source_lang,
        tgt_lang=req.target_lang
    )[0]["translation_text"]

    return {"translation": translation}

@app.post("/embed")
async def embed_text(req: TextRequest):
    """
    Generate embedding vector for input text using SentenceTransformer.

    Args:
        req (TextRequest): Request containing the input text.

    Returns:
        dict: Embedding vector.
    """
    embedding = sentence_embedder.encode(req.text).tolist()
    return {"embedding": embedding}

@app.post("/rerank")
async def rerank_texts(req: BatchTextRequest):
    """
    Rerank multiple documents using FlashReranker model.

    Args:
        req (BatchTextRequest): Request containing query text and documents.

    Returns:
        dict: Top reranked documents.
    """
    input_docs = [{"text": doc.combined_text} for doc in req.documents]

    if not any(doc["text"] for doc in input_docs):
        return {"rerank": []}

    try:
        scores = flash_reranker.score(req.text, input_docs)
    except Exception as e:
        logger.error(f"Reranker model scoring failed: {e}")
        return {"rerank": []}

    scored_docs = []
    for doc, score in zip(req.documents, scores):
        scored_docs.append({
            "id": doc.id,
            "original_score": doc.score,
            "rerank_score": score,
            "combined_text": doc.combined_text
        })

    return {"rerank": scored_docs}

@app.api_route("/ollama/{path:path}", methods=["GET", "POST"])
async def proxy_to_ollama(path: str, request: Request):
    """
    Forward any /ollama/* request to the Ollama server running inside container.
    """
    url = f"http://localhost:11434/{path}"

    try:
        # Copy headers except for host
        headers = dict(request.headers)
        headers.pop("host", None)

        # Create a new client session
        async with httpx.AsyncClient() as client:
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=request.query_params)
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(url, headers=headers, content=body)

        # Stream response back
        if "stream" in response.headers.get("content-type", ""):
            return StreamingResponse(response.aiter_raw(), status_code=response.status_code, headers=response.headers)
        else:
            return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.error(f"Error forwarding request to Ollama: {e}")
        return JSONResponse(content={"error": "Failed to forward request to Ollama."}, status_code=500)

@app.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 OK if server process is alive.
    """
    return {"status": "ok"}

@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    Verifies that all critical models are loaded and application is ready.
    """
    try:
        if not all([
            whisper_model,
            whisper_processor,
            nllb_translator,
            sentence_embedder,
            flash_reranker
        ]):
            raise ValueError("One or more models are not loaded.")
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(status_code=500, content={"status": "not ready", "detail": str(e)})
