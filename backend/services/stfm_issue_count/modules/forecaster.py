import httpx
from config.config import config

class ModelForecaster:
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
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                text = await response.text()
                raise Exception(f"Model server error: {text}")
            data = response.json()
        return data.get("predictions")
