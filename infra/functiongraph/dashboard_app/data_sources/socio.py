# --- data_sources/socio.py ---
import requests
from utils.config import ONEMAP_API_KEY, ONEMAP_SOCIO_URL

def get_socioeconomic_data(planning_area):
    headers = {"Authorization": ONEMAP_API_KEY}
    resp = requests.get(f"{ONEMAP_SOCIO_URL}?planningArea={planning_area}&year=2020", headers=headers)
    return resp.json()
