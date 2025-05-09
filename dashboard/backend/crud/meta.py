from dashboard.backend.db.database import pool

async def get_issue_types():
    query = """
        SELECT it.name AS type, isc.name AS subtype
        FROM issue_types it
        LEFT JOIN issue_subtypes isc ON it.issue_type_id = isc.issue_type_id
        ORDER BY it.name, isc.name
    """
    async with pool.connection() as conn:
        result = await conn.execute(query)
        rows = await result.fetchall()
    grouped = {}
    for row in rows:
        grouped.setdefault(row["type"], []).append(row["subtype"]) if row["subtype"] else grouped.setdefault(row["type"], [])
    return grouped

async def get_agencies():
    query = "SELECT agency_name FROM agencies ORDER BY agency_name"
    async with pool.connection() as conn:
        result = await conn.execute(query)
        rows = await result.fetchall()
    return [r["agency_name"] for r in rows]

async def get_town_councils():
    query = "SELECT council_name FROM town_councils ORDER BY council_name"
    async with pool.connection() as conn:
        result = await conn.execute(query)
        rows = await result.fetchall()
    return [r["council_name"] for r in rows]
