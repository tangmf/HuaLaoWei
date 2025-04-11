#!/usr/bin/env python3

"""
Open-Meteo Weather + Air Quality Fetcher (Threaded + Fully Configurable)

Required installations:
- pip install pandas
- pip install pyyaml
- pip install requests
"""

import os
import csv
import yaml
import time
import logging
import warnings
import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Optional, Dict, List

warnings.simplefilter(action="ignore", category=FutureWarning)

# Constants
WEATHER_API_BASE = "https://archive-api.open-meteo.com/v1/archive"
AIR_API_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"
csv_lock = Lock()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --------------------------
# Load config
# --------------------------
def load_config_from_yaml(yaml_path: str, key: str) -> dict:
    with open(yaml_path, "r") as f:
        all_configs = yaml.safe_load(f)
    if key not in all_configs:
        raise KeyError(f"Configuration for '{key}' not found in {yaml_path}")
    return all_configs[key]

# --------------------------
# Date parser
# --------------------------
def parse_and_round_datetime(date_str: str) -> Optional[datetime]:
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d-%m-%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return (dt + timedelta(hours=1)) if dt.minute >= 30 else dt.replace(minute=0, second=0, microsecond=0)
        except ValueError:
            continue
    logging.warning(f"Invalid date format: {date_str}")
    return None

# --------------------------
# Build Open-Meteo URL
# --------------------------
def build_openmeteo_url(base_url: str, lat: float, lon: float, start_date: str, end_date: str, query: Dict) -> str:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
    }
    for key, val in query.items():
        if isinstance(val, list):
            if val:
                params[key] = ",".join(val)
        elif val is not None:
            params[key] = val
    return base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

# --------------------------
# Fetch data for single row
# --------------------------
def fetch_hourly_data(lat: float, lon: float, report_dt: datetime, config: dict) -> Optional[pd.DataFrame]:
    hours_before = config.get("hours_before", 0)
    hours_after = config.get("hours_after", 0)
    start_dt = report_dt - timedelta(hours=hours_before)
    end_dt = report_dt + timedelta(hours=hours_after)

    start_date = config.get("start_date") or start_dt.strftime("%Y-%m-%d")
    end_date = config.get("end_date") or end_dt.strftime("%Y-%m-%d")

    try:
        weather_url = build_openmeteo_url(
            WEATHER_API_BASE, lat, lon, start_date, end_date, config["weather_api"]["query"]
        )
        air_url = build_openmeteo_url(
            AIR_API_BASE, lat, lon, start_date, end_date, config["air_api"]["query"]
        )

        weather = requests.get(weather_url)
        air = requests.get(air_url)
        weather.raise_for_status()
        air.raise_for_status()

        df_weather = pd.DataFrame(weather.json().get("hourly", {}))
        df_air = pd.DataFrame(air.json().get("hourly", {}))

        if df_weather.empty:
            logging.warning(f"No weather data for ({lat},{lon})")
            return None

        df_weather["time"] = pd.to_datetime(df_weather["time"])
        if not df_air.empty:
            df_air["time"] = pd.to_datetime(df_air["time"])
        df = pd.merge(df_weather, df_air, on="time", how="left")
        df = df[(df["time"] >= start_dt) & (df["time"] <= end_dt)]
        return df

    except requests.RequestException as e:
        logging.error(f"Failed to fetch data for ({lat},{lon}) — {e}")
        return None

# --------------------------
# Process single row
# --------------------------
def process_row(row, config: dict) -> List[List]:
    id_vals = [row[col] for col in config["keep_cols"]]
    lat = row[config["lat_col"]]
    lon = row[config["lon_col"]]
    date_str = row[config["date_col"]]
    report_dt = parse_and_round_datetime(date_str)

    if pd.isna(lat) or pd.isna(lon) or report_dt is None:
        logging.warning(f"Skipping row {id_vals} due to missing or invalid data")
        return []

    for attempt in range(config["max_retries"]):
        df = fetch_hourly_data(lat, lon, report_dt, config)
        if df is not None:
            results = []
            for _, row_ in df.iterrows():
                row_data = id_vals + [lat, lon, date_str, row_["time"]]
                for col in df.columns:
                    if col != "time":
                        row_data.append(row_.get(col, "NA"))
                results.append(row_data)
            return results
        time.sleep(config["backoff"] ** attempt)

    logging.error(f"All attempts failed for {id_vals}")
    return []

# --------------------------
# Bulk threaded execution
# --------------------------
def process_csv_bulk(config: dict):
    df = pd.read_csv(config["input_csv"])
    first_success = None

    with ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
        futures = [executor.submit(process_row, row, config) for _, row in df.iterrows()]

        with open(config["output_csv"], "a", newline="") as f:
            writer = csv.writer(f)

            for future in as_completed(futures):
                result = future.result()
                if result:
                    # Write header dynamically only once
                    if first_success is None:
                        first_success = result[0]
                        header = config["keep_cols"] + ["weather_datetime"]
                        header += [col for col in result[0][len(header):]]
                        writer.writerow(header)
                    with csv_lock:
                        for row in result:
                            writer.writerow(row)

# --------------------------
# Script Entry
# --------------------------
if __name__ == "__main__":
    config_key = "openmeteo_us_newyork"
    yaml_path = "config.yaml"

    config = load_config_from_yaml(yaml_path, config_key)
    if not os.path.exists(config["output_csv"]):
        with open(config["output_csv"], "w") as _: pass  # Create file if not exists

    process_csv_bulk(config)
