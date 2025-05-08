from mobile_app.backend.db.database import pool
from psycopg.rows import dict_row

async def get_user_posts(user_id: int):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM forum_posts WHERE user_id = %s",
                (user_id,)
            )
            posts = await cur.fetchall()
            return posts
