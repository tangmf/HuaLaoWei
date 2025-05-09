"""
session.py

A core module for the HuaLaoWei municipal chatbot.
Manages chat session logging and retrieval for chatbot conversations using a PostgreSQL database.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import json
from datetime import datetime, timezone
import psycopg2
from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Chat Session Logger
# --------------------------------------------------------

class ChatSessionLogger:
    """
    ChatSessionLogger provides methods to log and retrieve chat messages 
    associated with user sessions into a PostgreSQL database.
    """

    def __init__(self):
        self.env = config.env

        try:
            self.rds_config = config.data_stores.relational_db
            self.rds_host = self.rds_config.host
            self.rds_port = self.rds_config.port
            self.rds_database = self.rds_config.database
            self.rds_user = self.rds_config.user
            self.rds_password = self.rds_config.password
            self.rds_ssl = self.rds_config.ssl
        except AttributeError:
            raise ValueError("Relational Database configurations missing in config")

        try:
            self.conn = psycopg2.connect(
                host=self.rds_host,
                port=self.rds_port,
                database=self.rds_database,
                user=self.rds_user,
                password=self.rds_password,
                sslmode="require" if self.rds_ssl else "disable"
            )
            self.conn.autocommit = True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise

        logger.info(f"Connected to PostgreSQL at {self.rds_host}:{self.rds_port}")


    def log_message(
        self,
        session_id: str,
        user_id: str,
        sender: str,
        message: str,
        message_type: str = "text",
        metadata: dict = None
    ) -> None:
        """
        Log a single chat message into the database.

        Args:
            session_id (str): Unique session identifier.
            user_id (str): Unique user identifier.
            sender (str): Sender of the message ("user" or "assistant").
            message (str): Message text content.
            message_type (str, optional): Type of the message. Defaults to "text".
            metadata (dict, optional): Optional metadata. Defaults to None.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Logging message: session_id={session_id}, user_id={user_id}, sender={sender}")

        try:
            with self.conn.cursor() as cur:
                cur.execute(
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
        except Exception as e:
            logger.error(f"Failed to insert chat session message into database: {str(e)}")

    def get_structured_messages(
        self,
        session_id: str,
        user_id: str = None,
        max_messages: int = 10
    ) -> list[dict]:
        """
        Retrieve a structured list of chat messages for a given session.

        Args:
            session_id (str): Unique session identifier.
            user_id (str, optional): User identifier to filter by. Defaults to None.
            max_messages (int, optional): Maximum number of recent messages. Defaults to 10.

        Returns:
            list[dict]: Structured list of chat messages with "role" and "content".
        """
        logger.debug(f"Structuring last {max_messages} messages for session {session_id}")

        messages = self._get_session_messages(session_id, user_id)
        messages = messages[-max_messages:] if messages else []

        chat_log = []
        for sender, message, message_type, created_at, metadata in messages:
            if message_type != "text":
                continue
            role = "user" if sender == "user" else "assistant"
            chat_log.append({"role": role, "content": message})

        return chat_log

    # --------------------------------------------------------
    # Private Helper Methods
    # --------------------------------------------------------

    def _get_session_messages(
        self,
        session_id: str,
        user_id: str = None
    ) -> list:
        """
        Private helper to fetch all messages for a session from the database.

        Args:
            session_id (str): Unique session identifier.
            user_id (str, optional): User identifier to filter by. Defaults to None.

        Returns:
            list: List of database message rows.
        """
        logger.info(f"Fetching messages for session: {session_id}")

        try:
            with self.conn.cursor() as cur:
                if user_id:
                    cur.execute(
                        """
                        SELECT sender, message, message_type, created_at, metadata
                        FROM chat_sessions
                        WHERE session_id = %s AND user_id = %s
                        ORDER BY created_at ASC
                        """,
                        (session_id, user_id)
                    )
                else:
                    cur.execute(
                        """
                        SELECT sender, message, message_type, created_at, metadata
                        FROM chat_sessions
                        WHERE session_id = %s AND user_id IS NULL
                        ORDER BY created_at ASC
                        """,
                        (session_id,)
                    )

                return cur.fetchall()

        except Exception as e:
            logger.error(f"Failed to fetch session messages: {str(e)}")
            return []
