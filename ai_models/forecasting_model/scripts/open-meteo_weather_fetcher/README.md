# Open-Meteo Historical Weather and Air Quality Fetcher

This script fetches **historical hourly weather** and **air quality data** from the [Open-Meteo API](https://open-meteo.com/) for each report in a municipal dataset. It uses a **threaded architecture** for efficiency, supports **flexible configuration**, and is designed to integrate cleanly into open data processing pipelines.

---

## Features

- Multi-threaded fetching with retry logic
- Works with single-key or multi-key `id_cols`
- Configurable `hours_before` and `hours_after` window per report
- Dynamically constructs API queries with support for:
  - `hourly` and `daily` variables
  - Unit preferences (temperature, wind, precipitation, etc.)
  - Timezone and model options
- External `config.yaml` for maximum control (no code editing required)
- Auto-generated CSV headers based on selected variables

---

## File Structure

```
project/
├── openmeteo_fetcher.py
├── config.yaml
├── us/
│   └── weather_us_newyork_open-meteo.csv # Output example
├── municipal_reports/
│   └── us/
│       └── municipal_us_newyork_311.csv  # Input example
```

---

## Installation

Install the required Python packages:

```bash
pip install pandas pyyaml requests
```

---

## Configuration (`config.yaml`)

Define one or more cities with their parameters. Here is an example for New York City:

```yaml
us_newyork:
  country: "us"
  city: "newyork"

  input_csv: "../municipal_reports/us/municipal_us_newyork_311.csv"
  output_csv: "us/weather_us_newyork_open-meteo.csv"

  keep_cols: ["unique_key", "boundary_name", "latitude", "longitude", "created_date"] 
  lat_col: "latitude"
  lon_col: "longitude"
  date_col: "created_date"

  hours_before: 23
  hours_after: 0
  
  max_workers: 25
  max_retries: 3
  backoff: 2 

  weather_api:
    query:
      hourly:
        - temperature_2m
        - relative_humidity_2m
        - precipitation
        - windspeed_10m
      daily: null
      timezone: "UTC"

  air_api:
    query:
      hourly:
        - pm10
        - pm2_5
        - carbon_monoxide
        - nitrogen_dioxide
        - ozone
        - sulphur_dioxide
      timezone: "UTC"
```

---

## Running the Script

```bash
python openmeteo_fetcher.py
```

Make sure the `config.yaml` contains a valid key like `us_newyork`, and update the `config_key` inside the script.

---

## Output Format

The output is a CSV file (e.g., `us/weather_us_sanfrancisco_open-meteo.csv`) with the following structure:

```
unique_key,latitude,longitude,issue_datetime,weather_datetime,temp,precip,pm10,pm2_5,...
```

- Each input report expands into **multiple rows**: one per timestamp within the specified window.
- Columns are automatically generated from `hourly` and `daily` variables configured in `config.yaml`.

---

## Notes and Tips

- You can specify which columns from the input file you want to retain in the output file via **`keep_cols`** (e.g., `["service_id", "agency"]`).
- **Weather and Air APIs** are queried independently and merged by timestamp.
- You may reduce `max_workers` if encountering rate limits or API throttling.

---

## Open-Meteo API References

- [Historical Weather API Docs](https://open-meteo.com/en/docs/historical-weather-api)
- [Historical Air Quality API Docs](https://open-meteo.com/en/docs/historical-air-quality-api)

---
