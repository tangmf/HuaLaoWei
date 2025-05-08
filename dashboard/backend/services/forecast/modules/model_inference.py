import aiohttp
import os
from config.config import config

class ModelInferenceService:
    def __init__(self):
        self.env = config.env

        try:
            self.forecast_url = config.ai_models.forecast_model_issue_count.url
        except AttributeError:
            raise ValueError("Forecasting issue count model url missing in config")
        
    async def forecast_issue_counts(self, issue_type_name: str, feature_matrix: list):
        url = f"{self.forecast_url}forecast/tcn"
        payload = {
            "issueTypeName": issue_type_name,
            "features": feature_matrix
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Model server error: {text}")
                data = await response.json()
        return data.get("predictions")
