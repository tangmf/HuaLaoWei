import json
from backend.data_stores.resources import Resources
from psycopg.rows import dict_row
from datetime import datetime, timezone

async def log_message(resources: Resources, session_id: str, user_id: str, sender: str, message: str, message_type: str = "text", metadata: dict = None):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                    """
                    INSERT INTO chat_sessions (session_id, user_id, sender, message, message_type, metadata, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        user_id,
                        sender,
                        message,
                        message_type,
                        json.dumps(metadata) if metadata else None,
                        datetime.now(timezone.utc)
                    )
                )
            log_data = await cur.fetchone()
            return log_data

async def get_session_messages(resources: Resources, session_id: str, user_id: str = None):
    async with resources.db_client.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            if user_id:
                await cur.execute(
                    """
                    SELECT sender, message, message_type, created_at, metadata
                    FROM chat_sessions
                    WHERE session_id = %s AND user_id = %s
                    ORDER BY created_at ASC
                    """,
                    (session_id, user_id)
                )
            else:
                await cur.execute(
                    """
                    SELECT sender, message, message_type, created_at, metadata
                    FROM chat_sessions
                    WHERE session_id = %s AND user_id IS NULL
                    ORDER BY created_at ASC
                    """,
                    (session_id,)
                )
                
            return await cur.fetchall()
        

