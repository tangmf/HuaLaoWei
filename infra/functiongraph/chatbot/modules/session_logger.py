from datetime import datetime
import psycopg2
import os
import uuid
import json

class ChatSessionLogger:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            sslmode="require" if os.getenv("PGSSL", "false").lower() == "true" else "disable"
        )
        self.conn.autocommit = True

    def log_message(self, session_id, user_id, sender, message, message_type="text", metadata=None):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_sessions (session_id, user_id, sender, message, message_type, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                user_id,
                sender,
                message,
                message_type,
                json.dumps(metadata) if metadata else None,
                datetime.utcnow()
            ))

    def get_session_messages(self, session_id, user_id=None):
        with self.conn.cursor() as cur:
            if user_id is not None:
                cur.execute("""
                    SELECT sender, message, message_type, created_at, metadata
                    FROM chat_sessions
                    WHERE session_id = %s AND user_id = %s
                    ORDER BY created_at ASC
                """, (session_id, user_id))
            else:
                cur.execute("""
                    SELECT sender, message, message_type, created_at, metadata
                    FROM chat_sessions
                    WHERE session_id = %s AND user_id IS NULL
                    ORDER BY created_at ASC
                """, (session_id,))
            return cur.fetchall()
        
    def get_structured_messages(self, session_id, user_id=None, max_messages=10):
        messages = self.get_session_messages(session_id, user_id)
        messages = messages[-max_messages:]

        chat_log = []
        for sender, message, message_type, created_at, metadata in messages:
            if message_type != "text":
                continue
            role = "user" if sender == "user" else "assistant"
            chat_log.append({"role": role, "content": message})
        return chat_log