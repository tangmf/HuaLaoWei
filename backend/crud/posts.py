from backend.data_stores.resources import Resources
from psycopg.rows import dict_row

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
