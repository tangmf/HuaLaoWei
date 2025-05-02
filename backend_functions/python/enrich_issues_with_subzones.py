import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, Point
import re
import json

# ---------- Helper Function ----------
def extract_from_description(description: str, key: str) -> str:
    pattern = f"<th>{key}</th> <td>(.*?)</td>"
    match = re.search(pattern, description)
    return match.group(1).strip() if match else None

# ---------- Load and Parse GeoJSONs ----------
with open("2019_SG_Subzone.geojson", "r") as f:
    subzone_data = json.load(f)

with open("2019_SG_PlnArea.geojson", "r") as f:
    planning_area_data = json.load(f)

# ---------- Extract Subzones ----------
subzone_records = []
subzone_id_counter = 1
for feature in subzone_data["features"]:
    desc = feature["properties"]["Description"]
    name = extract_from_description(desc, "SUBZONE_N")
    if name:
        geom = shape(feature["geometry"])
        subzone_records.append({
            "subzone_id": subzone_id_counter,
            "subzone_name": name,
            "geometry": geom
        })
        subzone_id_counter += 1

subzone_gdf = gpd.GeoDataFrame(subzone_records, crs="EPSG:4326")

# ---------- Extract Planning Areas ----------
planning_area_records = []
planning_area_id_counter = 1
for feature in planning_area_data["features"]:
    desc = feature["properties"]["Description"]
    name = extract_from_description(desc, "PLN_AREA_N")
    if name:
        geom = shape(feature["geometry"])
        planning_area_records.append({
            "planning_area_id": planning_area_id_counter,
            "planning_area_name": name,
            "geometry": geom
        })
        planning_area_id_counter += 1

planning_area_gdf = gpd.GeoDataFrame(planning_area_records, crs="EPSG:4326")

# ---------- Load Issues Table ----------
issues_df = pd.read_csv("issues.csv")
issues_gdf = gpd.GeoDataFrame(
    issues_df,
    geometry=gpd.points_from_xy(issues_df.longitude, issues_df.latitude),
    crs="EPSG:4326"
)

# ---------- Spatial Join ----------
issues_with_subzone = gpd.sjoin(
    issues_gdf,
    subzone_gdf[["subzone_id", "geometry"]],
    how="left",
    predicate="within"
)

issues_with_all = gpd.sjoin(
    issues_with_subzone,
    planning_area_gdf[["planning_area_id", "geometry"]],
    how="left",
    predicate="within",
    lsuffix='subzone',
    rsuffix='planning'
)

# ---------- Final Cleanup ----------
columns_to_drop = [col for col in ["geometry", "index_right_subzone", "index_right_planning"] if col in issues_with_all.columns]
final_issues_df = issues_with_all.drop(columns=columns_to_drop)

final_issues_df["subzone_id"] = final_issues_df["subzone_id"].fillna(-1).astype(int)
final_issues_df["planning_area_id"] = final_issues_df["planning_area_id"].fillna(-1).astype(int)

# ---------- Save Output ----------
final_issues_df.to_csv("simulated_issues_singapore_with_subzones.csv", index=False)
print("✅ Enriched CSV saved as simulated_issues_singapore_with_subzones.csv")
