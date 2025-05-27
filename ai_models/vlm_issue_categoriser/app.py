"""
app.py

FastAPI server to host HuaLaoWei VLM Issue Categoriser.

Author: Jerick Cheong
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import json
from typing import Optional, List

import torch
from accelerate import Accelerator
from fastapi import FastAPI, Form, File, UploadFile
from pydantic import BaseModel
from peft import PeftModel
from transformers import AutoProcessor, AutoModelForImageTextToText

from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Constants
# --------------------------------------------------------

accelerator = Accelerator()
device = accelerator.device

# Global model and processor
vlm_processor = None
vlm_model = None

# --------------------------------------------------------
# Model Loading
# --------------------------------------------------------

def preload_vlm_model():
    """
    Preloads the VLM Issue Categoriser model and processor into memory.
    """
    global vlm_processor, vlm_model

    logger.info("Loading VLM Issue Categoriser model...")

    try:
        model_name = config.ai_models.vlm_issue_categoriser.model
        adapter_name = config.ai_models.vlm_issue_categoriser.adapter
    except AttributeError:
        raise ValueError("VLM Issue Categoriser model or adapter missing in config")

    vlm_processor = AutoProcessor.from_pretrained(model_name)
    base_model = AutoModelForImageTextToText.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
    )
    vlm_model = PeftModel.from_pretrained(base_model, adapter_name).to(device)
    vlm_model.eval()

    logger.info("VLM Issue Categoriser model loaded successfully.")

# --------------------------------------------------------
# FastAPI Setup
# --------------------------------------------------------

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    preload_vlm_model()

# --------------------------------------------------------
# Request Models
# --------------------------------------------------------

class InferRequest(BaseModel):
    messages: str
    classes: List[str]

# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def extract_assistant_response(decoded_output: str) -> dict:
    """
    Extracts and validates the assistant's JSON response from the model output.
    """
    assistant_start = decoded_output.find("Assistant:") + len("Assistant:")
    assistant_response = decoded_output[assistant_start:].strip()

    try:
        response_json = json.loads(assistant_response)
        if (
            "categories" not in response_json
            or "severity" not in response_json
            or not isinstance(response_json["categories"], list)
            or not isinstance(response_json["severity"], str)
        ):
            raise ValueError("Invalid response format.")
        return response_json
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the model response.")

def validate_response_categories(response: dict, valid_classes: List[str]) -> dict:
    """
    Ensures only allowed categories and valid severity are kept.
    """
    filtered_categories = [cat for cat in response["categories"] if cat in valid_classes]
    severity = response["severity"] if response["severity"] in ["Low", "Medium", "High"] else None

    return {
        "categories": filtered_categories,
        "severity": severity
    }

# --------------------------------------------------------
# API Endpoints
# --------------------------------------------------------

@app.post("/issue_categoriser")
async def infer(
    messages: str = Form(...),
    classes: str = Form(...),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Accepts text and optional images to perform issue categorisation using VLM.
    """
    try:
        images = files or [torch.zeros((1, 3, 224, 224), dtype=torch.uint8)]  # Dummy tensor if no images

        prompt = vlm_processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
        )
        inputs = vlm_processor(
            text=prompt,
            images=images,
            return_tensors="pt",
            padding=True
        ).to(device)

        with torch.no_grad():
            output = vlm_model.generate(**inputs)

        decoded_output = vlm_processor.decode(output[0], skip_special_tokens=True)
        assistant_response = extract_assistant_response(decoded_output)

        # Validate categories
        valid_classes = json.loads(classes) if isinstance(classes, str) else classes
        validated_response = validate_response_categories(assistant_response, valid_classes)

        return validated_response

    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        if vlm_processor is None or vlm_model is None:
            return {"status": "error", "message": "Model not loaded."}
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
