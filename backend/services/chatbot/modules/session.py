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
from datetime import datetime, timezone
from backend.data_stores.resources import Resources
from backend.crud import chatbot as crud_chatbot

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
        pass

    async def log_message(
        self,
        resources: Resources,
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
            await crud_chatbot.log_message(resources=resources, session_id=session_id, user_id=user_id, sender=sender, message=message, message_type=message_type, metadata=metadata)
        
        except Exception as e:
            logger.error(f"Failed to insert chat session message into database: {str(e)}")

    async def get_structured_messages(
        self,
        resources: Resources,
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

        messages = self._get_session_messages(resources, session_id, user_id)
        messages = messages[-max_messages:] if messages else []

        chat_log = []
        for sender, message, message_type, created_at, metadata in messages:
            if message_type != "text":
                continue
            role = "user" if sender == "user" else "assistant"
            chat_log.append({"role": role, "content": message})

        return chat_log

    async def _get_session_messages(
        self,
        resources: Resources,
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
            return await crud_chatbot.get_session_messages(resources=resources, session_id=session_id, user_id=user_id)

        except Exception as e:
            logger.error(f"Failed to fetch session messages: {str(e)}")
            return []
