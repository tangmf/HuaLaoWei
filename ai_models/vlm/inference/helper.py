from PIL import Image
import piexif
import requests

RELEVANT_KEYS = {
    'name', 'place', 'amenity', 'landuse', 'leisure', 'building',
    'highway', 'natural', 'shop', 'tourism', 'man_made', 'railway'
}

def filter_tags(tags: list[dict], useful_keys: set[str]) -> list[dict]:
    """
    Filter a list of tag dictionaries to keep only useful keys.

    Parameters:
        tags (list[dict]): A list of dictionaries containing tag key-value pairs.
        useful_keys (set[str]): A set of tag keys to keep.

    Returns:
        list[dict]: A new list of dictionaries with only the useful keys retained.
    """
    return [
        filtered_tag
        for tag in tags
        if (filtered_tag := {k: v for k, v in tag.items() if k in useful_keys})
    ]


def get_osm_tags_from_openstreetmap(lat, lon, radius=15, filter=True):
    overpass_url = "https://overpass-api.de/api/interpreter"
    tags = {"nearby": [], "enclosing": []}

    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        print("Invalid latitude or longitude values.")
        return tags
    
    # Define bounding box for out+geom (slightly expanded around the point)
    lat_min = lat - 0.0015
    lat_max = lat + 0.0015
    lon_min = lon - 0.0015
    lon_max = lon + 0.0015
    bbox = f"{lat_min},{lon_min},{lat_max},{lon_max}"

    # Nearby query
    nearby_query = f"""
    [timeout:10][out:json];
    (
      node(around:{radius},{lat},{lon});
      way(around:{radius},{lat},{lon});
    );
    out tags geom({bbox});
    relation(around:{radius},{lat},{lon});
    out geom({bbox});
    """

    # Enclosing query
    enclosing_query = f"""
    [timeout:10][out:json];
    is_in({lat},{lon})->.a;
    way(pivot.a);
    out tags bb;
    out ids geom({bbox});
    relation(pivot.a);
    out tags bb;
    """

    def run_query(query):
        response = requests.post(overpass_url, data={"data": query})
        response.raise_for_status()
        return response.json()

    try:
        nearby_data = run_query(nearby_query)
        enclosing_data = run_query(enclosing_query)
    except requests.exceptions.RequestException as e:
        print("Error querying Overpass API:", e)
        return tags


    # Collect tags from nearby results
    for element in nearby_data.get("elements", []):
        if "tags" in element:
            tags["nearby"].append(element["tags"])

    # Collect tags from enclosing results
    for element in enclosing_data.get("elements", []):
        if "tags" in element:
            tags["enclosing"].append(element["tags"])

    if filter:
        tags["nearby"] = filter_tags(tags["nearby"], RELEVANT_KEYS)
        tags["enclosing"] = filter_tags(tags["enclosing"], RELEVANT_KEYS)

    return tags


def get_decimal_from_dms(dms, ref):
    degrees, minutes, seconds = dms
    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_lat_lon(img):
    exif_dict = piexif.load(img.info['exif'])

    gps_data = exif_dict.get('GPS')
    if not gps_data:
        return None

    gps_latitude = gps_data.get(piexif.GPSIFD.GPSLatitude)
    gps_latitude_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef)
    gps_longitude = gps_data.get(piexif.GPSIFD.GPSLongitude)
    gps_longitude_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef)

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = get_decimal_from_dms(
            [val[0] / val[1] for val in gps_latitude],
            gps_latitude_ref.decode()
        )
        lon = get_decimal_from_dms(
            [val[0] / val[1] for val in gps_longitude],
            gps_longitude_ref.decode()
        )
        return lat, lon
    else:
        return None, None
    print("No GPS data found.")