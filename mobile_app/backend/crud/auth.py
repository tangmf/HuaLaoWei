from mobile_app.backend.db.database import pool
from psycopg.rows import dict_row

async def create_user(user: dict):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id",
                (user["username"], user["email"], user["password_hash"])
            )
            new_user = await cur.fetchone()
            return new_user

async def authenticate_user(user: dict):
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM users WHERE username = %s AND password_hash = %s",
                (user["username"], user["password_hash"])
            )
            user_data = await cur.fetchone()
            return user_data
