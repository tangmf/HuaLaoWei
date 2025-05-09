from backend.data_stores.resources import Resources
from psycopg.rows import dict_row

async def get_authorities(resources: Resources, params: dict):
    filters, values = [], []

    def add_filter(condition: str, value):
        filters.append(condition.replace("{}", "%s"))
        values.append(value)

    if params.get("authority_type"):
        add_filter("authority_type = {}", params["authority_type"])

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT authority_id, authority_type, authority_ref_id, name, description
        FROM authorities
        {where_clause}
        ORDER BY name ASC
    """

    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, values)
            return await cur.fetchall()


async def fetch_agency_id_from_name(resources: Resources, name: str) -> int | None:
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT agency_id FROM agencies WHERE name = %s",
                (name,)
            )
            row = await cur.fetchone()
            return row["agency_id"] if row else None

async def fetch_town_council_id_from_name(resources: Resources, name: str) -> int | None:
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT town_council_id FROM town_councils WHERE name = %s",
                (name,)
            )
            row = await cur.fetchone()
            return row["town_council_id"] if row else None
