from dashboard.backend.db.database import pool

async def get_planning_area(subzone_name: str):
    query = """
        SELECT p.name AS planning_area
        FROM subzones s
        JOIN planning_areas p ON s.planning_area_id = p.planning_area_id
        WHERE s.name = $1
    """
    async with pool.connection() as conn:
        result = await conn.execute(query, [subzone_name])
        row = await result.fetchone()
    return {"planning_area": row["planning_area"]} if row else None

async def fetch_subzone_centroid(subzone_name: str):
    query = """
        SELECT ST_Y(ST_Centroid(geom::geometry)) AS latitude,
               ST_X(ST_Centroid(geom::geometry)) AS longitude
        FROM subzones
        WHERE name = $1
        LIMIT 1
    """
    async with pool.connection() as conn:
        result = await conn.execute(query, [subzone_name])
        row = await result.fetchone()
    return (row["latitude"], row["longitude"]) if row else None

async def fetch_planning_area_by_subzone(subzone_name: str):
    query = """
        SELECT pa.name
        FROM subzones sz
        JOIN planning_areas pa ON sz.planning_area_id = pa.planning_area_id
        WHERE sz.name = $1
        LIMIT 1
    """
    async with pool.connection() as conn:
        result = await conn.execute(query, [subzone_name])
        row = await result.fetchone()
    return row["name"] if row else None
