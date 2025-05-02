# --- model/predictor.py ---
import torch
from pytorch_forecasting import TemporalFusionTransformer
from utils.config import MODEL_PATH

def load_model():
    model = TemporalFusionTransformer.load_from_checkpoint(MODEL_PATH)
    model.eval()
    return model

def forecast_issue_counts(model, df):
    predictions = model.predict(df)
    return predictions.detach().cpu().numpy().flatten()
