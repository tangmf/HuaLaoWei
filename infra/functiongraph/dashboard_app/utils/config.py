import os

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
ONEMAP_SOCIO_URL = "https://www.onemap.gov.sg/api/public/popapi/getHouseholdMonthlyIncomeWork"
ONEMAP_API_KEY = os.environ.get("ONEMAP_API_KEY")
MODEL_PATH = "tft_model_checkpoint.pth"