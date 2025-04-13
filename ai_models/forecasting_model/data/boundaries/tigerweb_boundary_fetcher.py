#!/usr/bin/env python3

"""
TIGERWeb Boundary Fetcher and Point Mapper

- Fetches boundaries from TIGERWeb based on FIPS
- Supports custom cluster or region grouping
- Optionally dissolves geometries
- Reads input CSV of lat/lon points and maps each to GEOID, region, etc.
- Outputs boundary file and point-level CSV mapping
"""

import os
import yaml
import logging
import requests
import geojson
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, Point
from typing import List

# --------------------------
# Logging Setup
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --------------------------
# Load config
# --------------------------
def load_config(path: str, key: str) -> dict:
    with open(path, 'r') as f:
        cfg = yaml.safe_load(f)
    if key not in cfg:
        raise KeyError(f"Missing key '{key}' in config")
    return cfg[key]

# --------------------------
# Fetch TIGERWeb boundaries
# --------------------------
def get_tigerweb_boundaries(state_fips, county_fips=None, layer_id=8, epsg=4326) -> gpd.GeoDataFrame:
    logging.info(f"Fetching TIGERWeb: state={state_fips}, county={county_fips or 'ALL'}, layer={layer_id}")
    endpoint = f'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer/{layer_id}/query'

    params = {
        'outFields': '*',
        'f': 'geojson',
        'outSR': epsg,
        'geometryType': 'esriGeometryEnvelope',
        'spatialRel': 'esriSpatialRelIntersects',
        'inSR': epsg
    }

    if county_fips:
        params['where'] = f"STATE='{state_fips}' AND COUNTY='{county_fips}'"
    else:
        params['geometry'] = "-123.1738,37.6391,-122.2818,37.9298"
        params['where'] = f"STATE='{state_fips}'"

    features = []
    offset = 0
    while True:
        resp = requests.get(endpoint, params={**params, 'resultOffset': offset, 'resultRecordCount': 1000})
        resp.raise_for_status()
        batch = geojson.loads(resp.text).get("features", [])
        if not batch:
            break
        features.extend(batch)
        logging.info(f"Fetched {len(batch)} features (total: {len(features)})")
        offset += len(batch)

    if not features:
        raise Exception("No features found. Check FIPS or layer ID.")

    geometries = [shape(f["geometry"]) for f in features if f.get("geometry")]
    props = [f["properties"] for f in features if f.get("properties")]
    return gpd.GeoDataFrame(props, geometry=geometries, crs=f"EPSG:{epsg}")

# --------------------------
# Combine and annotate boundaries
# --------------------------
def fetch_combined_boundaries(fips_list: List[dict], layer_id: int) -> gpd.GeoDataFrame:
    dfs = []
    for entry in fips_list:
        state = entry["state"]
        county = entry.get("county")
        cluster = entry.get("cluster")
        gdf = get_tigerweb_boundaries(state, county, layer_id)
        if not gdf.empty and cluster:
            gdf["cluster"] = cluster
        dfs.append(gdf)
    return gpd.GeoDataFrame(pd.concat(dfs).reset_index(drop=True)) if dfs else gpd.GeoDataFrame()

def apply_custom_regions(gdf: gpd.GeoDataFrame, region_def: dict, fallback_label: str = None) -> gpd.GeoDataFrame:
    gdf["GEOID"] = gdf["GEOID"].astype(str)
    gdf["region"] = None
    for region_name, geoid_list in region_def.items():
        gdf.loc[gdf["GEOID"].isin(geoid_list), "region"] = region_name

    unmatched = gdf["region"].isna().sum()
    if fallback_label:
        gdf["region"] = gdf["region"].fillna(fallback_label)
        logging.info(f"Assigned fallback region '{fallback_label}' to {unmatched} tracts")

    return gdf

# --------------------------
# Save output boundary file
# --------------------------
def save_boundary_file(gdf: gpd.GeoDataFrame, path: str, fmt: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if fmt.lower() == "geojson":
        gdf.to_file(path, driver="GeoJSON")
    elif fmt.lower() in ["shp", "shapefile"]:
        gdf.to_file(path, driver="ESRI Shapefile")
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    logging.info(f"Saved boundary file to {path}")

# --------------------------
# Read and spatially map input points
# --------------------------
def map_points_to_boundaries(input_csv: str, keep_cols: List[str], 
                              boundaries: gpd.GeoDataFrame, output_csv: str):
    df = pd.read_csv(input_csv, low_memory=False)
    df["geometry"] = df.apply(lambda row: Point(row[lon_col], row[lat_col]), axis=1)
    gdf_points = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # Spatial join
    joined = gpd.sjoin(gdf_points, boundaries, how="left", predicate="within")

    output_cols = keep_cols + ["GEOID"]
    if "region" in joined.columns:
        output_cols.append("region")
    if "cluster" in joined.columns:
        output_cols.append("cluster")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    joined[output_cols].to_csv(output_csv, index=False)
    logging.info(f"Saved point mapping to: {output_csv}")

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    CONFIG_PATH = "config.yaml"
    CONFIG_KEY = "us_chicago"

    config = load_config(CONFIG_PATH, CONFIG_KEY)

    fips_list = config["fips"]
    layer_id = config.get("tigerweb", {}).get("layer_id", 8)
    output_geo = config["output_geo"]
    output_geo_format = config.get("output_geo_format", "geojson")
    dissolve_by = config.get("dissolve_by")
    custom_regions = config.get("custom_regions", {})
    skip_unassigned = config.get("skip_unassigned", False)
    fallback_label = config.get("unassigned_label")

    # CSV point input
    input_csv = config.get("input_csv")
    output_csv = config.get("output_csv")
    keep_cols = config.get("keep_cols", ["id"])
    lat_col = config.get("latitude", "latitude")
    lon_col = config.get("longitude", "longitude")

    # Step 1: Fetch all boundaries
    gdf = fetch_combined_boundaries(fips_list, layer_id)

    # Step 2: Apply custom region labels
    if custom_regions:
        gdf = apply_custom_regions(gdf, custom_regions, fallback_label)
        logging.info(f"Applied region labels: {gdf['region'].dropna().nunique()} regions")

    # Step 3: Optional dissolve
    if dissolve_by:
        if dissolve_by not in gdf.columns:
            raise ValueError(f"'dissolve_by: {dissolve_by}' failed — column not found.")
        if skip_unassigned:
            gdf = gdf[~gdf[dissolve_by].isna()].copy()
        elif fallback_label:
            gdf[dissolve_by] = gdf[dissolve_by].fillna(fallback_label)
        gdf = gdf.dissolve(by=dissolve_by, as_index=False)
        logging.info(f"Dissolved boundaries by '{dissolve_by}' → {len(gdf)} total regions")

    # Step 4: Save boundaries
    os.makedirs(os.path.dirname(output_geo), exist_ok=True)
    save_boundary_file(gdf, output_geo, output_geo_format)

    # Step 5: Map input CSV points to boundaries
    if input_csv and output_csv:
        map_points_to_boundaries(input_csv, keep_cols, gdf, output_csv)
