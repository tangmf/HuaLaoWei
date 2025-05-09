from backend.data_stores.resources import Resources
from psycopg.rows import dict_row

async def get_region_from_lat_lng(resources: Resources, lat: float, lng: float) -> dict | None:
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    subzones.subzone_id,
                    subzones.name AS subzone_name,
                    subzones.geom AS subzone_geom,
                    subzones.area_sq_m AS subzone_area,
                    planning_areas.planning_area_id,
                    planning_areas.name AS planning_area_name,
                    planning_areas.geom AS planning_area_geom,
                    planning_areas.area_sq_m AS planning_area_area
                FROM subzones
                JOIN planning_areas ON subzones.planning_area_id = planning_areas.planning_area_id
                WHERE ST_Contains(subzones.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
                LIMIT 1
                """,
                (lng, lat)
            )
            return await cur.fetchone()
        

async def get_planning_area_info_from_subzone(resources: Resources, params: dict):
    """
    {
        "planning_area_id": <integer>,
        "planning_area_name": <string>,
        "description": <string or None>
    }
    """
    filters, values = [], []

    def add_filter(condition: str, value):
        filters.append(condition.replace("{}", "%s"))
        values.append(value)

    if "subzone_id" in params:
        add_filter("sz.subzone_id = {}", params["subzone_id"])
    elif "subzone_name" in params:
        add_filter("sz.name = {}", params["subzone_name"])
    else:
        raise ValueError("Must provide either 'subzone_id' or 'subzone_name'.")

    where_clause = f"WHERE {' AND '.join(filters)}"

    query = f"""
        SELECT pa.planning_area_id, pa.name AS planning_area_name, pa.description
        FROM subzones sz
        JOIN planning_areas pa ON sz.planning_area_id = pa.planning_area_id
        {where_clause}
        LIMIT 1
    """

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, values)
            return await cur.fetchone()


async def get_planning_area_centroid(resources: Resources, params: dict):
    filters, values = [], []

    def add_filter(condition: str, value):
        filters.append(condition.replace("{}", "%s"))
        values.append(value)

    if "planning_area_id" in params:
        add_filter("planning_area_id = {}", params["planning_area_id"])
    elif "planning_area_name" in params:
        add_filter("name = {}", params["planning_area_name"])
    else:
        raise ValueError("Must provide either 'planning_area_id' or 'planning_area_name'.")

    where_clause = f"WHERE {' AND '.join(filters)}"

    query = f"""
        SELECT ST_Y(ST_Centroid(geom::geometry)) AS latitude,
               ST_X(ST_Centroid(geom::geometry)) AS longitude
        FROM planning_areas
        {where_clause}
    """

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, values)
            return await cur.fetchone()


async def get_subzone_centroid(resources: Resources, params: dict):
    """
    {
        "latitude": <float>,
        "longitude": <float>
    }
    """
    filters, values = [], []

    def add_filter(condition: str, value):
        filters.append(condition.replace("{}", "%s"))
        values.append(value)

    if "subzone_id" in params:
        add_filter("subzone_id = {}", params["subzone_id"])
    elif "subzone_name" in params:
        add_filter("name = {}", params["subzone_name"])
    else:
        raise ValueError("Must provide either 'subzone_id' or 'subzone_name'.")

    where_clause = f"WHERE {' AND '.join(filters)}"

    query = f"""
        SELECT ST_Y(ST_Centroid(geom::geometry)) AS latitude,
               ST_X(ST_Centroid(geom::geometry)) AS longitude
        FROM subzones
        {where_clause}
    """

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, values)
            return await cur.fetchone()
