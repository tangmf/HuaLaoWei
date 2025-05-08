from mobile_app.backend.db.database import pool
from psycopg.rows import dict_row

async def fetch_agency_id_from_name(name: str) -> int | None:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT agency_id FROM agencies WHERE name = %s",
                (name,)
            )
            row = await cur.fetchone()
            return row["agency_id"] if row else None

async def fetch_town_council_id_from_name(name: str) -> int | None:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT town_council_id FROM town_councils WHERE name = %s",
                (name,)
            )
            row = await cur.fetchone()
            return row["town_council_id"] if row else None
