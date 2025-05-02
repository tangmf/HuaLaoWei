# routers/tcn_router.py

from fastapi import APIRouter
from pydantic import BaseModel
import torch
import numpy as np
from loaders.model_loader import model_cache
from config import DEVICE
from datetime import datetime, timedelta

router = APIRouter(prefix="/forecast", tags=["TCN Models"])

class ForecastRequest(BaseModel):
    issueTypeName: str
    features: list

@router.post("/tcn")
def forecast_tcn(request: ForecastRequest):
    print(request)
    try:
        cached = model_cache.get(request.issueTypeName)

        if cached is None:
            return {"error": f"Model for issue type '{request.issueTypeName}' not found."}

        model, expected_input_size = cached

        features = request.features
        
        if isinstance(features[0], dict):
            input_matrix = []
            original_features = features  # Save original features
            for feature_dict in features:
                row = []
                for value in feature_dict.values():
                    if value is None:
                        row.append(0.0)
                    elif isinstance(value, bool):
                        row.append(float(value))
                    else:
                        row.append(float(value))
                input_matrix.append(row)
        else:
            input_matrix = [features]
            original_features = [{"feature_" + str(i): v for i, v in enumerate(features)}]

        input_size = len(input_matrix[0])

        if input_size != expected_input_size:
            return {"error": f"Input size mismatch. Expected {expected_input_size}, got {input_size}."}

        input_tensor = torch.tensor(input_matrix, dtype=torch.float32).unsqueeze(2).to(DEVICE)
        preds = []

        with torch.no_grad():
            for i in range(0, len(input_tensor), 64):
                batch_X = input_tensor[i:i+64]
                batch_preds = model(batch_X)
                preds.append(batch_preds.cpu().numpy())

        preds = np.vstack(preds).flatten().tolist()

        # Build the output: list of dicts
        results = []
        today = datetime.today()
        for idx, prediction in enumerate(preds):
            forecast_date = today + timedelta(days=idx)
            results.append({
                "forecastDate": forecast_date.strftime("%Y-%m-%d"),
                "features": original_features[idx] if idx < len(original_features) else {},
                "forecast_value": prediction
            })
        
        return {"predictions": results}

    except Exception as e:
        print(e)
        return {"error": str(e)}


@router.get("/health")
def tcn_health_check():
    try:
        if not model_cache:
            return {"status": "error", "message": "No models loaded."}

        model_info = []
        for issue_type, (model, input_size) in model_cache.items():
            model_info.append({
                "issueTypeName": issue_type,
                "expectedInputSize": input_size
            })

        return {
            "status": "ok",
            "modelCount": len(model_cache),
            "models": model_info
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
