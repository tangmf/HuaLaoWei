from mobile_app.backend.data_stores.resources import Resources
from psycopg.rows import dict_row

async def get_user_posts(resources: Resources, user_id: int):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM forum_posts WHERE user_id = %s",
                (user_id,)
            )
            posts = await cur.fetchall()
            return posts
