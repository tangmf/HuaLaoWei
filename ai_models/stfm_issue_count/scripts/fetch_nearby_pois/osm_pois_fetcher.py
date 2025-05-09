#!/usr/bin/env python3

"""
POI Enrichment Script (YAML-Driven, Multi-Radius, Configurable Output)

- Loads issue reports with lat/lon
- Fetches OSM POIs using bounding box and tags
- Computes density and distance for each POI category and radius

Required installations:
- pip install geopandas
- pip install osmnx
- pip install scikit-learn
"""

import os
import yaml
import logging
import pandas as pd
import geopandas as gpd
import numpy as np
import osmnx as ox
from sklearn.neighbors import KDTree

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
        config = yaml.safe_load(f)
    if key not in config:
        raise KeyError(f"Missing config block: {key}")
    return config[key]

# ----------------------------
# Fetch POIs from OSM
# ----------------------------
def get_pois(bbox, tags) -> gpd.GeoDataFrame:
    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        polygon = ox.utils_geo.bbox_to_poly((min_lon, min_lat, max_lon, max_lat))
        pois = ox.features.features_from_polygon(polygon, tags=tags)

        if pois.empty:
            logging.warning(f"No POIs found for tags: {tags}")
            return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326").to_crs(epsg=3857)

        pois = pois[pois.geometry.notnull()].copy()
        pois["geometry"] = pois.geometry.apply(lambda g: g.centroid if g.geom_type != "Point" else g)
        return pois.to_crs(epsg=3857)

    except Exception as e:
        logging.error(f"Failed to fetch POIs: {e}")
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326").to_crs(epsg=3857)

# ----------------------------
# Density within buffer
# ----------------------------
def compute_density(issues_gdf, pois_gdf, radius_m):
    if pois_gdf.empty:
        return pd.Series(0, index=issues_gdf.index)

    issues_valid = issues_gdf[issues_gdf.geometry.notnull()].copy()
    issues_valid["buffer"] = issues_valid.geometry.buffer(radius_m)
    buffer_geoms = issues_valid["buffer"]

    # Build spatial index on POIs
    sidx = pois_gdf.sindex

    # For each buffer, count how many POIs are inside
    counts = []
    for geom in buffer_geoms:
        matches = list(sidx.query(geom, predicate="intersects"))
        counts.append(len(matches))

    return pd.Series(counts, index=issues_valid.index).reindex(issues_gdf.index).fillna(0).astype(int)


# ----------------------------
# Nearest distance to POI
# ----------------------------
def compute_proximity(issues_gdf, pois_gdf):
    if pois_gdf.empty:
        return np.full(len(issues_gdf), np.nan)

    valid = issues_gdf.geometry.notnull()
    x = issues_gdf.geometry.x
    y = issues_gdf.geometry.y
    valid &= x.notnull() & y.notnull() & np.isfinite(x) & np.isfinite(y)

    issues_valid = issues_gdf[valid].copy()
    if issues_valid.empty:
        return np.full(len(issues_gdf), np.nan)

    issue_coords = np.vstack([issues_valid.geometry.x, issues_valid.geometry.y]).T
    poi_coords = np.vstack([pois_gdf.geometry.x, pois_gdf.geometry.y]).T

    tree = KDTree(poi_coords)
    distances, _ = tree.query(issue_coords, k=1)

    out_series = pd.Series(data=distances.flatten(), index=issues_valid.index)
    return out_series.reindex(issues_gdf.index).fillna(np.nan).values

# ----------------------------
# Enrichment Pipeline
# ----------------------------
def enrich_issues_with_pois(cfg: dict):
    city = cfg["city"]
    input_csv = cfg["input_csv"]
    output_csv = cfg["output_csv"]
    lat_col = cfg["latitude"]
    lon_col = cfg["longitude"]
    keep_map = cfg["keep_cols"]
    radius_list = cfg.get("radius_m", [200])
    bbox = cfg.get("bounding_box")
    tags_dict = cfg["poi_tags"]

    logging.info(f"Processing city: {city}, input: {input_csv}")

    df = pd.read_csv(input_csv)
    for col in list(keep_map.keys()):
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    gdf_issues = gpd.GeoDataFrame(
        df[list(keep_map.keys())].copy(),
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)

    all_features = []

    if not bbox:
        logging.info("No bounding box provided. Deriving from issue locations...")
        minx, miny, maxx, maxy = gdf_issues.total_bounds  # in EPSG:3857
        bounds_poly = gdf_issues.to_crs(epsg=4326).total_bounds  # Convert to EPSG:4326
        min_lat, min_lon, max_lat, max_lon = bounds_poly[1], bounds_poly[0], bounds_poly[3], bounds_poly[2]
        bbox = [min_lat, min_lon, max_lat, max_lon]
        logging.info(f"Auto-derived bounding box: {bbox}")

    for category, tags in tags_dict.items():
        logging.info(f"Fetching POIs for category '{category}'...")
        pois = get_pois(bbox, tags)
        proximity = compute_proximity(gdf_issues, pois)
        gdf_issues[f"dist_to_nearest_{category}_in_m"] = proximity

        for radius in radius_list:
            col = f"{category}_count_within_{radius}m"
            density = compute_density(gdf_issues, pois, radius)
            gdf_issues[col] = density
            all_features.append(col)

        all_features.append(f"dist_to_nearest_{category}_in_m")

    gdf_issues = gdf_issues.rename(columns=keep_map)
    final = gdf_issues[list(keep_map.values()) + all_features]
    logging.info(f"Generated columns: {gdf_issues.columns.tolist()}")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    final.to_csv(output_csv, index=False)
    logging.info(f"Saved enriched output to {output_csv}")

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    CONFIG_PATH = "config.yaml"
    CONFIG_KEY = "us_newyork"
    cfg = load_config(CONFIG_PATH, CONFIG_KEY)
    enrich_issues_with_pois(cfg)