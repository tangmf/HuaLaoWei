from backend.data_stores.resources import Resources
from psycopg.rows import dict_row
from datetime import datetime, timedelta

async def like_post(resources: Resources, user_id: int, post_id: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO post_votes (user_id, post_id) VALUES (%s, %s)",
                (user_id, post_id)
            )

async def create_post(resources: Resources, user_id: int, issue_id: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO forum_posts (user_id, issue_id) VALUES (%s, %s)",
                (user_id, issue_id)
            )

async def count_post_likes(resources: Resources, post_id: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM post_votes WHERE post_id = %s",
                (post_id,)
            )
            result = await cur.fetchone()
            return result["count"]

async def get_forum_posts(resources: Resources, user_lat: float, user_lon: float, radius_meters: int = 2000):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("""
                SELECT 
                    fp.post_id,
                    fp.issue_id,
                    fp.user_id,
                    fp.title,
                    fp.created_at,
                    i.latitude,
                    i.longitude,
                    i.severity,
                    i.status,
                    i.description,
                    ima.file_path
                FROM forum_posts fp
                JOIN issues i ON fp.issue_id = i.issue_id
                LEFT JOIN LATERAL (
                    SELECT file_path
                    FROM issue_media_assets
                    WHERE issue_id = i.issue_id AND media_type = 'image'
                    ORDER BY issue_media_id ASC
                    LIMIT 1
                ) ima ON true
                WHERE i.latitude IS NOT NULL 
                  AND i.longitude IS NOT NULL 
                  AND i.is_deleted = FALSE
                  AND fp.created_at >= NOW() - INTERVAL '7 days'
                  AND ST_DWithin(
                        i.location::geography,
                        ST_MakePoint(%s, %s)::geography,
                        %s
                    )
            """, (user_lon, user_lat, radius_meters))
            return await cur.fetchall()
