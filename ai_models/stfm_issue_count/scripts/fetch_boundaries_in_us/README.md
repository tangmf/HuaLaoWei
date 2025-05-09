# TIGERWeb Boundary Fetcher & Point Mapper

This script fetches U.S. Census TIGER boundaries from the [TIGERWeb ArcGIS API](https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_apps.html), and optionally maps a CSV of points (latitude/longitude) to the boundary polygons. It supports **custom grouping, enrichment, dissolve**, and **batch configs**.

---

## 📦 Features

- Fetch TIGERWeb boundaries (tracts, counties, etc.) by FIPS
- Group by custom `cluster` (county-level) or `region` (GEOID-level)
- Assign fallback labels for unmatched regions
- Optionally dissolve geometries by `region`, `cluster`, etc.
- Output boundaries as GeoJSON or Shapefile
- Map CSV points to `GEOID`, `region`, `cluster`
- Write point-to-boundary results to a separate output CSV
- Multi-key YAML config for batch use

---

## Configuration (`config.yaml`)

You can define multiple keys like so:

```yaml
us_chicago:
  fips:
    - { state: "17", county: "031", cluster: "chicago" }

  custom_regions:
    downtown:
      - "17031081200"
      - "17031081300"
    north_side:
      - "17031211200"
      - "17031211300"
    far_south:
      - "17031980000"
      - "17031980100"

  dissolve_by: null                              # Optional: set to 'region' to merge
  skip_unassigned: false                         # Optional: keep unmatched regions
  unassigned_label: "other_chicago_areas"        # Optional fallback label for unmatched

  tigerweb:
    layer_id: 8                                   # Census Tracts

  output_geo: "boundaries/boundaries_us_chicago.geojson"
  output_geo_format: "geojson"

  input_csv: "../municipal_reports/us/municipal_us_chicago_311.csv"
  output_csv: "us/boundaries_us_chicago.csv"

  keep_cols: ["sr_number", "created_date", "latitude", "longitude"]
  latitude: "latitude"
  longitude: "longitude"
```

---

## Region / Cluster / Dissolve Logic

| Config Key                  | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `custom_regions`            | Define GEOID-based groupings into named regions                            |
| `fips.cluster`              | Assigns a `cluster` label to all boundaries from a given (state, county)    |
| `dissolve_by`               | If set to `'region'` or `'cluster'`, will dissolve geometries by that label |
| `unassigned_label`          | Fills in unmatched `region` with this fallback label                        |
| `skip_unassigned`           | If true, removes unmatched geometries before dissolve                       |

🔹 Even if `dissolve_by` is `null`, fallback labels are now still applied.

---

## Input CSV Enrichment

If you provide `input_csv`, the script will:

- Read the CSV
- Map each lat/lon point to the polygon it falls into
- Append `GEOID`, `region`, `cluster` columns to it
- Output to `output_csv`

All spatial joins are done in **EPSG:4326**, and geometry columns are dropped from output.

---

## TIGERWeb Layer Reference

| Layer ID | Description            | Units Returned per Area      | Notes                                 |
|----------|------------------------|-------------------------------|----------------------------------------|
| `84`     | Counties               | 1 per county                 | Use for borough-level maps             |
| `8`      | Census Tracts          | ~200–800 per NYC borough     | Best for socioeconomic joins           |
| `82`     | Block Groups           | ~500–1,500 per borough       | More detailed than tracts              |
| `10`     | Census Blocks          | ~5,000+ per borough          | Highly detailed; usually overkill      |
| `86`     | County Subdivisions    | Varies                       | Towns/townships in non-NYC areas       |
| `91`     | ZIP Code Tab Areas     | 100–300 per borough          | Useful for public-facing maps          |

---

## NYC County/Borough Mapping

| Borough       | County Name     | County FIPS |
|---------------|------------------|-------------|
| Bronx         | Bronx            | `005`       |
| Brooklyn      | Kings            | `047`       |
| Manhattan     | New York         | `061`       |
| Queens        | Queens           | `081`       |
| Staten Island | Richmond         | `085`       |

---

## Usage

Edit this line in `tigerweb_boundary_fetcher.py`:

```python
CONFIG_KEY = "us_chicago"
```

Then run:

```bash
python tigerweb_boundary_fetcher.py
```

---

## Output Files

| Output           | Description                                           |
|------------------|-------------------------------------------------------|
| `output_geo`     | GeoJSON or Shapefile of boundary polygons             |
| `output_csv`     | CSV mapping each input point to GEOID, region, etc.   |

---

## Dependencies

```bash
pip install geopandas requests pyyaml shapely geojson
```

---

## Tips

- Use `dissolve_by: region` if you want one polygon per custom region.
- Use `dissolve_by: null` to preserve tract-level geometries but still apply region/cluster tags.
- Use `unassigned_label` to avoid empty regions in the output even when dissolve is off.
- Use `cluster` to label entire counties when GEOID-level grouping is not needed.

---

Need help building the right GEOID list for a region? Ask your assistant to help you generate them based on map previews, city planning data, or TIGER shapefiles.