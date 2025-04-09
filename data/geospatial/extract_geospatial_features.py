import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from sklearn.neighbors import KDTree
import osmnx as ox
import argparse
import sys
import yaml

# Optional bounding boxes (can help constrain area when not using place names)
CITY_BBOX = {
    'new_york': (40.4774, -74.2591, 40.9176, -73.7004),
    'san_francisco': (37.6398, -123.1738, 37.9298, -122.2818),
    'chicago': (41.6445, -87.9401, 42.0230, -87.5237)
}

TAGS_DICT = {
    'commercial': {
        'shop': True,
        'amenity': ['marketplace', 'mall']
    },
    'facilities': {
        'amenity': ['school', 'hospital']
    },
    'recreation': {
        'leisure': 'park',
        'tourism': True
    },
    'transit': {
        'highway': 'bus_stop',
        'railway': ['station', 'subway_entrance'],
        'public_transport': ['platform', 'stop_position']
    }
}

def get_pois(bbox, tags):
    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        polygon = ox.utils_geo.bbox_to_poly((min_lon, min_lat, max_lon, max_lat))
        pois = ox.features.features_from_polygon(polygon, tags=tags)

        if pois.empty:
            print(f"[WARNING] No POIs found for tags: {tags}")
            return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326").to_crs(epsg=3857)

        pois = pois[pois.geometry.notnull()].copy()
        pois['geometry'] = pois.geometry.apply(lambda geom: geom.centroid if geom.geom_type != "Point" else geom)
        pois = pois.to_crs(epsg=3857)

        print(f"  ↳ Total POIs: {len(pois)}")
        for tag_key, tag_val in tags.items():
            if tag_key in pois.columns:
                if tag_val is True:
                    print(f"    • {tag_key}=* → {pois[tag_key].notna().sum()}")
                elif isinstance(tag_val, list):
                    for val in tag_val:
                        print(f"    • {tag_key}={val} → {(pois[tag_key] == val).sum()}")
                else:
                    print(f"    • {tag_key}={tag_val} → {(pois[tag_key] == tag_val).sum()}")
            else:
                print(f"    • {tag_key} not found in POIs")

        return pois

    except Exception as e:
        print(f"[ERROR] Failed to fetch POIs for tags: {tags}\n{e}")
        empty = gpd.GeoDataFrame(geometry=[], crs="EPSG:4326").to_crs(epsg=3857)
        return empty

def compute_density(issues_gdf, pois_gdf, radius_m):
    issues_valid = issues_gdf[issues_gdf.geometry.notnull()].copy()
    buffer = issues_valid.copy()
    buffer['geometry'] = buffer.geometry.buffer(radius_m)

    if len(pois_gdf) == 0:
        print("[DEBUG] POI GeoDataFrame is empty. Returning all zeros.")
        return issues_gdf.index.to_series().map(lambda _: 0)

    issue_bounds = buffer.total_bounds
    poi_bounds = pois_gdf.total_bounds

    print(f"[DEBUG] Issue area bounds:   {issue_bounds}")
    print(f"[DEBUG] POI area bounds:     {poi_bounds}")

    issues_bbox = gpd.GeoSeries([Point(issue_bounds[0], issue_bounds[1]), Point(issue_bounds[2], issue_bounds[3])]).union_all().envelope
    pois_bbox = gpd.GeoSeries([Point(poi_bounds[0], poi_bounds[1]), Point(poi_bounds[2], poi_bounds[3])]).union_all().envelope
    intersects = issues_bbox.intersects(pois_bbox)

    if not intersects:
        print("[WARNING] No spatial overlap detected between issues and POIs. Counts will be all zeros.")
    else:
        print("[DEBUG] Issue and POI regions do overlap.")

    join = gpd.sjoin(pois_gdf, buffer, predicate='within', how='inner')
    counts = join.groupby('index_right').size()

    return issues_gdf.index.to_series().map(counts).fillna(0).astype(int)

def compute_proximity(issues_gdf, pois_gdf):
    if len(pois_gdf) == 0:
        return np.full(len(issues_gdf), np.nan)

    valid = issues_gdf.geometry.notnull()
    x = issues_gdf.geometry.x
    y = issues_gdf.geometry.y
    valid &= x.notnull() & y.notnull() & np.isfinite(x) & np.isfinite(y)

    issues_valid = issues_gdf[valid].copy()

    if len(issues_valid) == 0:
        return np.full(len(issues_gdf), np.nan)

    issue_coords = np.vstack([issues_valid.geometry.x, issues_valid.geometry.y]).T
    poi_coords = np.vstack([pois_gdf.geometry.x, pois_gdf.geometry.y]).T

    tree = KDTree(poi_coords)
    distances, _ = tree.query(issue_coords, k=1)

    out_series = pd.Series(data=distances.flatten(), index=issues_valid.index)
    return out_series.reindex(issues_gdf.index).fillna(np.nan).values

def enrich_issues_with_pois(input_csv, output_csv, city_name, lat_col, lon_col, id_col, radius_m=200):
    if city_name.lower() not in CITY_BBOX:
        print(f"City '{city_name}' is not supported. Choose from: {list(CITY_BBOX.keys())}")
        sys.exit(1)

    bbox = CITY_BBOX[city_name.lower()]
    print(f"Using bounding box for {city_name}: {bbox}")

    df_issues = pd.read_csv(input_csv, low_memory=False)
    required_cols = {lat_col, lon_col, id_col}
    if not required_cols.issubset(df_issues.columns):
        raise ValueError(f"CSV must contain these columns: {required_cols}")

    null_latlon = df_issues[[lat_col, lon_col]].isnull().sum()
    if null_latlon.any():
        print(f"[WARNING] Found {null_latlon.to_dict()} missing latitude/longitude values.")

    gdf_issues = gpd.GeoDataFrame(
        df_issues[[id_col, lat_col, lon_col]].copy(),
        geometry=gpd.points_from_xy(df_issues[lon_col], df_issues[lat_col]),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)

    null_geoms = gdf_issues.geometry.isnull().sum()
    if null_geoms > 0:
        print(f"[WARNING] {null_geoms} issues have missing coordinates and will be skipped in spatial analysis.")

    poi_dict = {}
    for category, tags in TAGS_DICT.items():
        print(f"Fetching POIs for category: {category}")
        poi_dict[category] = get_pois(bbox, tags)

    gdf_issues[f'commercial_count_within_{radius_m}m'] = compute_density(gdf_issues, poi_dict['commercial'], radius_m)
    gdf_issues['dist_to_nearest_commericial'] = compute_proximity(gdf_issues, poi_dict['commercial'])

    gdf_issues[f'recreation_count_within_{radius_m}m'] = compute_density(gdf_issues, poi_dict['recreation'], radius_m)
    gdf_issues['dist_to_nearest_recreation'] = compute_proximity(gdf_issues, poi_dict['recreation'])

    gdf_issues[f'facilities_count_within_{radius_m}m'] = compute_density(gdf_issues, poi_dict['facilities'], radius_m)
    gdf_issues['dist_to_nearest_facility'] = compute_proximity(gdf_issues, poi_dict['facilities'])

    gdf_issues[f'transit_count_within_{radius_m}m'] = compute_density(gdf_issues, poi_dict['transit'], radius_m)
    gdf_issues['dist_to_nearest_transit'] = compute_proximity(gdf_issues, poi_dict['transit'])

    result = gdf_issues[[id_col, lat_col, lon_col,
        f'commercial_count_within_{radius_m}m', 'dist_to_nearest_commericial',
        f'recreation_count_within_{radius_m}m', 'dist_to_nearest_recreation',
        f'facilities_count_within_{radius_m}m', 'dist_to_nearest_facility',
        f'transit_count_within_{radius_m}m', 'dist_to_nearest_transit']]
    result = result.rename(columns={id_col: "id"})
    
    result.to_csv(output_csv, index=False)
    print(f"Enriched dataset saved to {output_csv}")

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhance municipal issues with POI density and proximity features.")
    parser.add_argument("--input_csv", help="Input CSV file path")
    parser.add_argument("--output_csv", help="Output CSV file path")
    parser.add_argument("--city", choices=list(CITY_BBOX.keys()), help="City name")
    parser.add_argument("--lat_col", default="latitude", help="Column name for latitude")
    parser.add_argument("--lon_col", default="longitude", help="Column name for longitude")
    parser.add_argument("--id_col", default="id", help="Column name for unique ID")
    parser.add_argument("--radius_m", type=int, default=200, help="Buffer radius in meters")
    parser.add_argument("--config", help="Path to YAML config file")

    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
        enrich_issues_with_pois(
            config["input_csv"],
            config["output_csv"],
            config["city"],
            config.get("lat_col", "latitude"),
            config.get("lon_col", "longitude"),
            config.get("id_col", "id"),
            config.get("radius_m", 200)
        )
    else:
        if not (args.input_csv and args.output_csv and args.city):
            parser.error("If --config is not provided, you must specify --input_csv, --output_csv, and --city.")
        enrich_issues_with_pois(
            args.input_csv,
            args.output_csv,
            args.city,
            args.lat_col,
            args.lon_col,
            args.id_col,
            args.radius_m
        )
