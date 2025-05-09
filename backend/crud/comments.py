from backend.data_stores.resources import Resources
from psycopg.rows import dict_row

async def like_comment(resources: Resources, user_id: int, comment_id: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO comment_votes (user_id, comment_id) VALUES (%s, %s)",
                (user_id, comment_id)
            )

async def create_comment(resources: Resources, user_id: int, post_id: int, content: str, parent_comment_id: int = None):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO comments (user_id, post_id, parent_comment_id, content)
                VALUES (%s, %s, %s, %s)
                RETURNING comment_id
                """,
                (user_id, post_id, parent_comment_id, content)
            )
            new_comment = await cur.fetchone()
            return new_comment

async def count_comment_likes(resources: Resources, comment_id: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM comment_votes WHERE comment_id = %s",
                (comment_id,)
            )
            result = await cur.fetchone()
            return result["count"]
