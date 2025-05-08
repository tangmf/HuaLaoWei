from mobile_app.backend.db.database import pool
from psycopg.rows import dict_row

async def fetch_region_from_lat_lng(lat: float, lng: float) -> dict | None:
    async with pool.connection() as conn:
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