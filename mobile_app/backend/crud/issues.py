from mobile_app.backend.db.database import pool
from psycopg.rows import dict_row

async def fetch_issue_type_info_from_name(name: str) -> int | None:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM issue_types WHERE name = %s",
                (name,)
            )
            return await cur.fetchone()
    
async def fetch_issue_subtype_info_from_name(name: str) -> int | None:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM issue_subtypes WHERE name = %s",
                (name,)
            )
            return await cur.fetchone()
        
async def fetch_issue_subtype():
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT ist.issue_subtype_id, ist.name, ist.description, ist.issue_type_id
            FROM issue_subtypes ist
            ORDER BY ist.issue_subtype_id
        """)

async def fetch_issue_type_subtype_rows():
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT it.issue_type_id, it.name AS type_name, it.description AS type_description,
                   ist.issue_subtype_id, ist.name AS subtype_name, ist.description AS subtype_description
            FROM issue_types it
            LEFT JOIN issue_subtypes ist ON it.issue_type_id = ist.issue_type_id
            ORDER BY it.issue_type_id, ist.issue_subtype_id
        """)

async def get_issues_nearby(lat: float, lon: float, radius: int):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT 
                    i.*, 
                    fp.*, 
                    c.comment_id, 
                    c.parent_comment_id, 
                    c.content AS comment_content, 
                    c.created_at AS comment_created_at, 
                    COUNT(DISTINCT pv.user_id) AS post_likes, 
                    COUNT(DISTINCT c.comment_id) OVER (PARTITION BY fp.post_id) AS comment_count, 
                    COUNT(DISTINCT cv.user_id) AS comment_likes
                FROM issues i
                LEFT JOIN forum_posts fp ON i.issue_id = fp.issue_id
                LEFT JOIN comments c ON fp.post_id = c.post_id
                LEFT JOIN post_votes pv ON fp.post_id = pv.post_id
                LEFT JOIN comment_votes cv ON c.comment_id = cv.comment_id
                WHERE ST_DWithin(i.location, ST_MakePoint(%s, %s)::geography, %s)
                ORDER BY i.issue_id, fp.post_id, c.comment_id
                """,
                (lon, lat, radius)
            )
            rows = await cur.fetchall()
            return rows

async def create_issue(issue: dict):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO issues (latitude, longitude, location, address, description, severity, status, datetime_reported, datetime_updated, agency_id, town_council_id, subzone_id, planning_area_id, is_public) VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING issue_id",
                (issue["latitude"], issue["longitude"], issue["longitude"], issue["latitude"], issue["address"], issue["description"], issue["severity"], issue.get("status", "Reported"), issue.get("datetime_reported"), issue.get("datetime_updated"), issue.get("agency_id"), issue.get("town_council_id"), issue.get("subzone_id"), issue.get("planning_area_id"), issue.get("is_public", True))
            )
            new_issue = await cur.fetchone()
            issue_id = new_issue["issue_id"]
            if "issue_type_ids" in issue:
                await cur.executemany(
                    "INSERT INTO issue_type_to_issue_mapping (issue_id, issue_type_id) VALUES (%s, %s)",
                    [(issue_id, type_id) for type_id in issue["issue_type_ids"]]
                )
            if "issue_subtype_ids" in issue:
                await cur.executemany(
                    "INSERT INTO issue_subtype_to_issue_mapping (issue_id, issue_subtype_id) VALUES (%s, %s)",
                    [(issue_id, subtype_id) for subtype_id in issue["issue_subtype_ids"]]
                )
            return {"issue_id": issue_id}