#!/usr/bin/env python3

"""
U.S. Socioeconomic Enrichment Script (CSV-based, Auto-FIPS)
- Reads input CSV of points with GEOIDs and timestamps
- Automatically derives state/county FIPS from GEOIDs
- Fetches ACS data and merges socioeconomic features
"""

import os
import yaml
import logging
import pandas as pd
import censusdata

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

# ----------------------------
# Load YAML config
# ----------------------------
def load_config(path: str, key: str) -> dict:
    with open(path, 'r') as f:
        all_cfg = yaml.safe_load(f)
    if key not in all_cfg:
        raise KeyError(f"Key '{key}' not found in {path}")
    return all_cfg[key]

def get_nearest_year(val: int, valid_years: list[int]) -> int:
    return min(valid_years, key=lambda x: abs(x - val))

# ----------------------------
# Retrieve FIPS
# ----------------------------
def extract_unique_fips(df: pd.DataFrame, geoid_col: str) -> list[dict]:
    """
    Extracts (state, county) FIPS combinations from the GEOID column.
    """
    df[geoid_col] = df[geoid_col].astype(str)
    df["state"] = df[geoid_col].str[:2]
    df["county"] = df[geoid_col].str[2:5]
    unique_fips = df[["state", "county"]].drop_duplicates().to_dict(orient="records")
    logging.info(f"Detected {len(unique_fips)} unique FIPS regions: {unique_fips}")
    return unique_fips

# ----------------------------
# Fetch CENSUS Features
# ----------------------------
def get_census_data(fips_list, year) -> pd.DataFrame:
    dfs = []
    for entry in fips_list:
        try:
            geo = censusdata.censusgeo([('state', entry['state']), ('county', entry['county']), ('tract', '*')])
            fields = ['B19013_001E', 'B01003_001E', 'B01002_001E']
            df = censusdata.download('acs5', year, geo, fields)
            df.columns = ['median_income', 'total_population', 'average_age']
            df.index = df.index.map(lambda g: f"{g.geo[0][1]}{g.geo[1][1]}{g.geo[2][1].zfill(6)}")
            df.index.name = 'GEOID'
            dfs.append(df)
        except Exception as e:
            logging.warning(f"[Census API] {entry['state']}-{entry['county']}: {e}")
    return pd.concat(dfs) if dfs else pd.DataFrame()

# --------------------------
# Script Entry
# --------------------------
if __name__ == "__main__":
    CONFIG_PATH = "config.yaml"
    CONFIG_KEY = "us_sanfrancisco"

    config = load_config(CONFIG_PATH, CONFIG_KEY)

    input_csv = config["input_csv"]
    output_csv = config["output_csv"]
    keep_cols = config.get("keep_cols", ["id"])
    datetime_col = config["datetime"]
    geoid_col = config.get("geoid_col", "GEOID")

    logging.info("Loading input data...")
    df = pd.read_csv(input_csv, dtype={geoid_col: str})

    # Parse year
    df["year"] = pd.to_datetime(df[datetime_col], errors="coerce").dt.year
    most_common_year = df["year"].mode()[0]
    valid_years = list(range(2010, 2023))
    selected_year = get_nearest_year(most_common_year, valid_years)
    logging.info(f"Using ACS year: {selected_year}")

    # Remove any rows where GEOID is not exactly 11 digits
    df[geoid_col] = df[geoid_col].astype(str).str.replace(r"\.0$", "", regex=True)
    df = df[df[geoid_col].str.fullmatch(r"\d{11}")]

    # Auto-extract FIPS from GEOIDs
    fips_multi = extract_unique_fips(df, geoid_col)

    # Fetch ACS census data
    census_df = get_census_data(fips_multi, selected_year)

    # Merge on GEOID
    df[geoid_col] = df[geoid_col].astype(str)
    enriched = df.merge(census_df, how="left", left_on=geoid_col, right_index=True)

    # Select columns for output
    output_cols = keep_cols + [datetime_col, "median_income", "total_population", "average_age"]
    enriched = enriched[output_cols]

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    enriched.to_csv(output_csv, index=False)
    logging.info(f"Saved enriched data to: {output_csv}")
