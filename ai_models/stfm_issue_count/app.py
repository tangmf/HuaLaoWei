"""
app.py

FastAPI server to forecast issue counts using preloaded TCN models.

Author: Fleming Siow
Date: 5th May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any

import torch
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

from models.tcn_model import TCN

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Constants
# --------------------------------------------------------

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_DIR = "models"
DEFAULT_MODEL_PARAMS = {
    "num_channels": [32, 64, 128],
    "kernel_size": 3,
    "dropout": 0.3
}
INPUT_SIZE_HINT = 13  # Static for now

model_cache: Dict[str, Tuple[torch.nn.Module, int]] = {}

# --------------------------------------------------------
# Model Preloading
# --------------------------------------------------------

def load_model(issue_type: str, model_path: str) -> torch.nn.Module:
    """
    Loads a single model file and returns the instantiated model.
    """
    model = TCN(
        input_size=INPUT_SIZE_HINT,
        output_size=1,
        **DEFAULT_MODEL_PARAMS
    )
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

def preload_all_models():
    """
    Preloads all forecast models from the models folder into memory.
    """
    logger.info(f"Preloading forecast models from {MODEL_DIR}...")

    if not os.path.exists(MODEL_DIR):
        logger.error(f"Model directory not found: {MODEL_DIR}")
        return

    model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith("_model.pth")]

    if not model_files:
        logger.warning(f"No model files found in {MODEL_DIR}")
        return

    for filename in model_files:
        model_path = os.path.join(MODEL_DIR, filename)
        issue_type = filename.replace("_model.pth", "")

        try:
            model_instance = load_model(issue_type, model_path)
            model_cache[issue_type] = (model_instance, INPUT_SIZE_HINT)
            logger.info(f"Preloaded model for issue type '{issue_type}'.")
        except Exception as e:
            logger.error(f"Failed to load model '{filename}': {e}")

    logger.info(f"Finished preloading {len(model_cache)} models.")

# --------------------------------------------------------
# FastAPI Setup
# --------------------------------------------------------

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    preload_all_models()

# --------------------------------------------------------
# Request/Response Models
# --------------------------------------------------------

class ForecastRequest(BaseModel):
    issue_type_name: str
    features: List[Any]

# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def prepare_input(features: List[Any], expected_input_size: int) -> torch.Tensor:
    """
    Prepares the input tensor from the request features.
    Optimized using NumPy.
    """
    if isinstance(features[0], dict):
        input_matrix = np.array([
            [float(value) if value is not None else 0.0 for value in feature_dict.values()]
            for feature_dict in features
        ], dtype=np.float32)
    else:
        input_matrix = np.array([features], dtype=np.float32)

    if input_matrix.shape[1] != expected_input_size:
        raise ValueError(f"Input size mismatch. Expected {expected_input_size}, got {input_matrix.shape[1]}.")

    input_tensor = torch.from_numpy(input_matrix).unsqueeze(2).to(DEVICE)
    return input_tensor

def format_predictions(preds: List[float], original_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Formats the prediction output with forecast dates and features.
    """
    today = datetime.today()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(preds))]

    return [
        {
            "forecast_date": date,
            "features": original_features[i] if i < len(original_features) else {},
            "forecast_value": preds[i]
        }
        for i, date in enumerate(dates)
    ]


# --------------------------------------------------------
# API Endpoints
# --------------------------------------------------------

@app.post("/forecast_issue_counts")
def forecast_issue_counts(request: ForecastRequest):
    """
    Forecasts issue counts based on the selected issue type and input features.
    """
    try:
        cached = model_cache.get(request.issue_type_name)
        if cached is None:
            return {"error": f"Model for issue type '{request.issue_type_name}' not found."}

        model, expected_input_size = cached

        input_tensor = prepare_input(request.features, expected_input_size)

        preds = []
        with torch.no_grad():
            for i in range(0, len(input_tensor), 64):
                batch_X = input_tensor[i:i+64]
                batch_preds = model(batch_X)
                preds.append(batch_preds.cpu().numpy())

        preds = np.vstack(preds).flatten().tolist()

        # Handle original features for response
        original_features = (
            request.features if isinstance(request.features[0], dict)
            else [{"feature_" + str(i): v for i, v in enumerate(request.features)}]
        )

        results = format_predictions(preds, original_features)
        return {"predictions": results}

    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify models are loaded.
    """
    try:
        if not model_cache:
            return {"status": "error", "message": "No models loaded."}

        model_info = [
            {"issue_type_name": issue_type, "expected_input_size": input_size}
            for issue_type, (model, input_size) in model_cache.items()
        ]

        return {
            "status": "ok",
            "modelCount": len(model_cache),
            "models": model_info
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
