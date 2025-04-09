import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import csv
import time
import logging
import requests
from datetime import datetime, timedelta

# --------------------------
# Setup logging
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# --------------------------
# Parse and round datetime to nearest hour
# --------------------------
def parse_and_round_datetime(date_str):
    date_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d-%m-%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
    ]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.minute >= 30:
                dt += timedelta(hours=1)
            return dt.replace(minute=0, second=0, microsecond=0)
        except ValueError:
            continue
    logging.warning(f"Invalid date format: {date_str}")
    return None

# --------------------------
# Fetch 24h hourly weather + air quality from Open-Meteo
# --------------------------
def get_24h_hourly_weather(lat, lon, report_dt):
    start_dt = report_dt - timedelta(hours=24)
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M")
    end_str = report_dt.strftime("%Y-%m-%dT%H:%M")

    base_url = "https://archive-api.open-meteo.com/v1/archive"
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    weather_url = (
        f"{base_url}?latitude={lat}&longitude={lon}"
        f"&start_date={start_str[:10]}&end_date={end_str[:10]}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,windspeed_10m"
        f"&timezone=UTC"
    )

    air_url = (
        f"{air_url}?latitude={lat}&longitude={lon}"
        f"&start_date={start_str[:10]}&end_date={end_str[:10]}"
        f"&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,sulphur_dioxide"
        f"&timezone=UTC"
    )

    try:
        weather_resp = requests.get(weather_url)
        air_resp = requests.get(air_url)
        weather_resp.raise_for_status()
        air_resp.raise_for_status()

        weather_data = weather_resp.json()
        air_data = air_resp.json()

        if "hourly" not in weather_data or "hourly" not in air_data:
            logging.warning(f"Incomplete response for {lat},{lon}")
            return None

        df_weather = pd.DataFrame({
            "time": weather_data["hourly"]["time"],
            "temp": weather_data["hourly"]["temperature_2m"],
            "rhum": weather_data["hourly"]["relative_humidity_2m"],
            "prcp": weather_data["hourly"]["precipitation"],
            "wspd": weather_data["hourly"]["windspeed_10m"]
        })

        df_air = pd.DataFrame({
            "time": air_data["hourly"]["time"],
            "pm10": air_data["hourly"].get("pm10", ["NA"] * len(df_weather)),
            "pm2_5": air_data["hourly"].get("pm2_5", ["NA"] * len(df_weather)),
            "co": air_data["hourly"].get("carbon_monoxide", ["NA"] * len(df_weather)),
            "no2": air_data["hourly"].get("nitrogen_dioxide", ["NA"] * len(df_weather)),
            "o3": air_data["hourly"].get("ozone", ["NA"] * len(df_weather)),
            "so2": air_data["hourly"].get("sulphur_dioxide", ["NA"] * len(df_weather))
        })

        df_merged = pd.merge(df_weather, df_air, on="time", how="left")

        # Enforce exact 24-hour range
        df_merged["time"] = pd.to_datetime(df_merged["time"])
        df_merged = df_merged[(df_merged["time"] >= start_dt) & (df_merged["time"] <= report_dt)]

        return df_merged

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {lat},{lon}: {e}")
        return None

# --------------------------
# Bulk processing
# --------------------------
def fetch_bulk_openmeteo(input_csv, id_col, lat_col, lon_col, date_col,
                         output_file="openmeteo_data.csv", start_row=0, end_row=None):
    df = pd.read_csv(input_csv)
    if end_row is None:
        end_row = len(df)

    file_exists = False
    try:
        with open(output_file, mode="r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(output_file, mode="a" if file_exists else "w", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "id", "latitude", "longitude", "issue_datetime", "weather_datetime",
                "temp_c", "humidity", "wind_kph", "precip_mm",
                "pm10", "pm2_5", "co", "no2", "o3", "so2"
            ])

        for index, row in df.iloc[start_row:end_row].iterrows():
            id = row[id_col]
            lat = row[lat_col]
            lon = row[lon_col]
            datetime_str = row[date_col]
            report_dt = parse_and_round_datetime(datetime_str)

            if pd.isna(lat) or pd.isna(lon) or report_dt is None:
                logging.warning(f"Skipping row {index} due to missing or invalid data")
                continue

            logging.info(f"Fetching 24h weather + air quality for ID {id} at ({lat},{lon}) up to {report_dt}")
            hourly_df = get_24h_hourly_weather(lat, lon, report_dt)

            if hourly_df is not None:
                for _, weather_row in hourly_df.iterrows():
                    writer.writerow([
                        id, lat, lon, datetime_str, weather_row["time"],
                        weather_row.get("temp", "NA"),
                        weather_row.get("rhum", "NA"),
                        weather_row.get("wspd", "NA"),
                        weather_row.get("prcp", "NA"),
                        weather_row.get("pm10", "NA"),
                        weather_row.get("pm2_5", "NA"),
                        weather_row.get("co", "NA"),
                        weather_row.get("no2", "NA"),
                        weather_row.get("o3", "NA"),
                        weather_row.get("so2", "NA")
                    ])
            else:
                logging.info(f"No hourly data found for ID {id}")

            time.sleep(0.2)

# --------------------------
# Main script entry
# --------------------------
if __name__ == "__main__":
    country = "us" 
    city = "chicago" # sf, newyork, chicago
    id_col = "sr_number" # service_request_id, unique_key, sr_number
    lat_col = "latitude" # lat, latitude, latitude
    lon_col = "longitude" # long, longitude, longitude
    date_col = "created_date" # requested_datetime, created_date, created_date

    input_csv_path = f"../municipal_reports/{country}/{city}_311.csv"
    output_path = f"{country}/{city}_openmeteo.csv"

    start_row = 1000
    end_row = 10000

    fetch_bulk_openmeteo(
        input_csv=input_csv_path,
        id_col=id_col,
        lat_col=lat_col,
        lon_col=lon_col,
        date_col=date_col,
        output_file=output_path,
        start_row=start_row,
        end_row=end_row
    )
