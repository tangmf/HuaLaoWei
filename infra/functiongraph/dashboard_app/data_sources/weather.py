# --- data_sources/weather.py ---
import requests
from utils.config import OPEN_METEO_URL

def get_weather_forecast(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,windspeed_10m,ozone,pm10,pm2_5,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide",
        "forecast_days": 7,
        "timezone": "Asia/Singapore"
    }
    resp = requests.get(OPEN_METEO_URL, params=params)
    return resp.json()