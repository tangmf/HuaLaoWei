#!/usr/bin/env python3

"""
Latitude/Longitude Clustering Script

- Supports configurable clustering models (e.g., KMeans, DBSCAN, HDBSCAN)
- Reads input CSV with latitude and longitude
- Saves output CSV with cluster labels
- Outputs per-cluster centroid coordinates

Required installations:
- pip install pandas
- pip install numpy
- pip install scikit-learn
- pip install pyyaml
- pip install hdbscan      
"""

import os
import yaml
import hdbscan
import logging
import warnings
import numpy as np
import pandas as pd
from joblib import Memory
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler

warnings.simplefilter(action="ignore", category=FutureWarning)

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ----------------------------
# Load YAML config
# ----------------------------
def load_config(path: str, key: str) -> dict:
    with open(path, 'r') as f:
        cfg = yaml.safe_load(f)
    if key not in cfg:
        raise KeyError(f"Missing config block: {key}")
    return cfg[key]

# ----------------------------
# Clustering: KMeans
# ----------------------------
def run_kmeans(df: pd.DataFrame, lat_col: str, lon_col: str, params: dict) -> pd.Series:
    coords = df[[lat_col, lon_col]].values
    coords_scaled = StandardScaler().fit_transform(coords)
    logging.info(f"[KMeans] Params: {params}")
    model = KMeans(**params).fit(coords_scaled)
    return pd.Series(model.labels_, index=df.index)

# ----------------------------
# Clustering: DBSCAN
# ----------------------------
def run_dbscan(df: pd.DataFrame, lat_col: str, lon_col: str, params: dict) -> pd.Series:
    coords_rad = np.radians(df[[lat_col, lon_col]].values)
    kms_per_radian = 6371.0088
    eps_km = params.pop("eps_km", 0.5)
    eps_rad = eps_km / kms_per_radian
    logging.info(f"[DBSCAN] Params: {params}")
    model = DBSCAN(eps=eps_rad, **params).fit(coords_rad)
    return pd.Series(model.labels_, index=df.index)

# ----------------------------
# Clustering: HDBSCAN 
# ----------------------------
def run_hdbscan(df: pd.DataFrame, lat_col: str, lon_col: str, params: dict) -> pd.Series:
    coords = np.radians(df[[lat_col, lon_col]].values)

    min_cluster_size = params.pop("min_cluster_size", 10)
    min_samples = params.pop("min_samples", 5)
    metric = params.pop("metric", "haversine")
    use_approx = params.pop("use_approximate_predict", True)
    prediction_data = params.pop("prediction_data", True)
    gen_min_span_tree = params.pop("gen_min_span_tree", False)
    subsample_size = params.pop("subsample_size", 10000)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric=metric,
        approx_min_span_tree=True,
        gen_min_span_tree=gen_min_span_tree,
        prediction_data=prediction_data,
        **params
    )

    if use_approx:
        subsample_size = min(subsample_size, len(coords))
        idx_sample = np.random.choice(len(coords), subsample_size, replace=False)
        sample_coords = coords[idx_sample]

        logging.info(f"[HDBSCAN] Running approximate mode on subsample size={subsample_size}")
        clusterer.fit(sample_coords)
        labels, _ = hdbscan.approximate_predict(clusterer, coords)
    else:
        logging.info(f"[HDBSCAN] Running full .fit() mode (may consume large memory!)")
        clusterer.fit(coords)
        labels = clusterer.labels_

    return pd.Series(labels, index=df.index)


# ----------------------------
# Dispatch model runner
# ----------------------------
def run_clustering_model(name: str, df: pd.DataFrame, lat_col: str, lon_col: str, params: dict) -> pd.Series:
    logging.info(f"🚀 Running model: {name}")
    if name.lower() == "kmeans":
        return run_kmeans(df, lat_col, lon_col, params)
    elif name.lower() == "dbscan":
        return run_dbscan(df, lat_col, lon_col, params)
    elif name.lower() == "hdbscan":
        return run_hdbscan(df, lat_col, lon_col, params)
    else:
        raise ValueError(f"Unsupported model: {name}")

# ----------------------------
# Clustering Pipeline
# ----------------------------
def cluster_latlon_points(cfg: dict):
    df = pd.read_csv(cfg["input_csv"], low_memory=False)
    lat_col = cfg["latitude"]
    lon_col = cfg["longitude"]
    keep_cols = cfg.get("keep_cols", [])
    output_csv = cfg["output_csv"]
    cluster_summary_csv = cfg.get("output_centroids_csv")

    for col in [lat_col, lon_col] + keep_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    base_cols = list(dict.fromkeys(keep_cols + [lat_col, lon_col]))
    result = df[base_cols].copy()

    models = cfg.get("models", {})
    for model_name, model_cfg in models.items():
        params = model_cfg.get("params", {})
        label = model_cfg.get("label", f"cluster_{model_name}")
        result[label] = run_clustering_model(model_name, df, lat_col, lon_col, params)

        # Output centroids per cluster
        if cluster_summary_csv:
            centroids = (
                result[result[label] >= 0]
                .groupby(label)[[lat_col, lon_col]]
                .mean()
                .reset_index()
                .rename(columns={lat_col: "cluster_lat", lon_col: "cluster_lon"})
            )
            os.makedirs(os.path.dirname(cluster_summary_csv), exist_ok=True)
            centroids.to_csv(cluster_summary_csv.replace(".csv", f"_{model_name}.csv"), index=False)
            logging.info(f"Saved cluster centroid summary to {cluster_summary_csv.replace('.csv', f'_{model_name}.csv')}")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result.to_csv(output_csv, index=False)
    logging.info(f"Clustering output saved to {output_csv}")

# --------------------------
# Script Entry
# --------------------------
if __name__ == "__main__":
    CONFIG_PATH = "config.yaml"
    CONFIG_KEY = "us_sanfrancisco"
    cfg = load_config(CONFIG_PATH, CONFIG_KEY)
    cluster_latlon_points(cfg)
