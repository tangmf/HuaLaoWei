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
from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Optional, Dict, List

warnings.simplefilter(action="ignore", category=FutureWarning)

# Constants
WEATHER_API_BASE = "https://archive-api.open-meteo.com/v1/archive"
AIR_API_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"
csv_lock = Lock()
consec_429_lock = Lock()
consec_429_counter = {"count": 0}

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ----------------------------
# Utility Functions
# ----------------------------
def get_processed_ids(output_path: str, id_col: str) -> set:
    if not os.path.exists(output_path):
        return set()
    try:
        df = pd.read_csv(output_path, usecols=[id_col])
        return set(df[id_col].dropna().unique())
    except Exception as e:
        logging.warning(f"Failed to parse output file for deduplication: {e}")
        return set()

def load_config_from_yaml(yaml_path: str, key: str) -> dict:
    with open(yaml_path, "r") as f:
        all_configs = yaml.safe_load(f)
    if key not in all_configs:
        raise KeyError(f"Configuration for '{key}' not found in {yaml_path}")
    return all_configs[key]

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
        if isinstance(val, list) and val:
            params[key] = ",".join(val)
        elif val is not None:
            params[key] = val
    return base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

# --------------------------
# Fetch data for single row
# --------------------------
def fetch_hourly_data(lat: float, lon: float, report_dt: datetime, config: dict) -> tuple[Optional[pd.DataFrame], bool, bool]:
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
        if weather.status_code == 429:
            return None, False, True
        weather.raise_for_status()

        air = requests.get(air_url)
        if air.status_code == 429:
            return None, False, True
        air.raise_for_status()

        df_weather = pd.DataFrame(weather.json().get("hourly", {}))
        df_air = pd.DataFrame(air.json().get("hourly", {}))

        if df_weather.empty:
            return None, False, False

        df_weather["time"] = pd.to_datetime(df_weather["time"])
        if not df_air.empty:
            df_air["time"] = pd.to_datetime(df_air["time"])

        df = pd.merge(df_weather, df_air, on="time", how="left")
        df = df[(df["time"] >= start_dt) & (df["time"] <= end_dt)]
        return df, True, False

    except requests.RequestException as e:
        if isinstance(e.response, requests.Response) and e.response.status_code == 429:
            return None, False, True
        return None, False, False

# --------------------------
# Process single row
# --------------------------
def process_row(row, config: dict) -> tuple[List[List], bool, bool]:
    id_vals = [row[col] for col in config["keep_cols"]]
    lat = row[config["lat_col"]]
    lon = row[config["lon_col"]]
    date_str = row[config["date_col"]]
    report_dt = parse_and_round_datetime(date_str)

    if pd.isna(lat) or pd.isna(lon) or report_dt is None:
        return [], False, False

    for attempt in range(config["max_retries"]):
        with consec_429_lock:
            if consec_429_counter["count"] >= config["max_retries"]:
                return [], False, True

        df, success, retryable = fetch_hourly_data(lat, lon, report_dt, config)
        if success and df is not None:
            with consec_429_lock:
                consec_429_counter["count"] = 0
            results = []
            for _, row_ in df.iterrows():
                row_data = id_vals + [lat, lon, date_str, row_["time"]]
                for col in df.columns:
                    if col != "time":
                        row_data.append(row_.get(col, "NA"))
                results.append(row_data)
            return results, True, False
        elif retryable:
            with consec_429_lock:
                consec_429_counter["count"] += 1
                logging.warning(f"[429] Consecutive 429s: {consec_429_counter['count']}")
            time.sleep(config["backoff"] ** attempt)
        else:
            with consec_429_lock:
                consec_429_counter["count"] = 0
            break

    return [], False, retryable

# --------------------------
# Bulk threaded execution
# --------------------------
def process_csv_bulk(config: dict):
    id_col = config.get("id_col")
    df_input = pd.read_csv(config["input_csv"], low_memory=False)
    already_processed = get_processed_ids(config["output_csv"], id_col) if id_col else set()
    if id_col:
        df_input = df_input[~df_input[id_col].isin(already_processed)]
    if df_input.empty:
        logging.info("No new rows to process.")
        return

    logging.info(f"Total unprocessed rows to fetch: {len(df_input)}")
    total_appended = 0

    with ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
        futures = [executor.submit(process_row, row, config) for _, row in df_input.iterrows()]
        with open(config["output_csv"], "a", newline="") as f:
            writer = csv.writer(f)
            first_success = None

            for future in as_completed(futures):
                try:
                    result, success, retryable = future.result()
                except Exception as e:
                    logging.error(f"Unhandled exception: {e}")
                    continue

                if retryable and consec_429_counter["count"] >= config["max_retries"]:
                    logging.error("Stopping due to repeated 429 errors.")
                    break

                if result:
                    if first_success is None:
                        first_success = result[0]
                        header = config["keep_cols"] + ["latitude", "longitude", config["date_col"], "weather_datetime"]
                        header += [col for col in result[0][len(header):]]
                        writer.writerow(header)

                    with csv_lock:
                        for row in result:
                            writer.writerow(row)
                        total_appended += len(result)

    logging.info(f"Total rows added: {total_appended}")

# --------------------------
# Script Entry
# --------------------------
if __name__ == "__main__":
    config_key = "us_chicago"
    yaml_path = "config.yaml"
    config = load_config_from_yaml(yaml_path, config_key)
    os.makedirs(os.path.dirname(config["output_csv"]), exist_ok=True)
    process_csv_bulk(config)
