"""
ollama_loader.py

The main handler for the use of LLMs in the HuaLaoWei municipal chatbot pipeline.
Handles interaction with a local or remote Ollama LLM server,
including request sending and response cleaning.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import re
import requests
import logging
from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Ollama Loader
# --------------------------------------------------------

class OllamaLoader:
    """
    OllamaLoader provides a simple interface to communicate with a local or hosted Ollama LLM server.
    """

    def __init__(self):
        self.env = config.env

        try:
            self.ollama_url = config.ai_models.chatbot.ollama.url
        except AttributeError:
            raise ValueError("Ollama service host url missing in config")

        logger.info(f"Loading Ollama service from: {self.ollama_url}")

    def generate(self, prompt_or_messages: list, model: str = "deepseek:7b") -> str:
        """
        Send a prompt or message list to the LLM server and return the model's response.

        Args:
            prompt_or_messages (list): List of message dictionaries (role and content).
            model (str, optional): Model name. Defaults to "deepseek:7b".

        Returns:
            str: Cleaned LLM response text.
        """
        payload = {
            "model": model,
            "messages": prompt_or_messages,
            "stream": False
        }
        endpoint = f"{self.ollama_url}/api/chat"

        logger.debug(f"Sending request to LLM at {endpoint}")

        try:
            response = requests.post(endpoint, json=payload, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to LLM server: {e}")
            raise RuntimeError(f"Failed to connect to LLM server: {e}")

        result = response.json()

        return self._parse_response(result)

    # --------------------------------------------------------
    # Private Helper Methods
    # --------------------------------------------------------

    def _parse_response(self, result: dict) -> str:
        """
        Private helper to parse and extract content from LLM server response.

        Args:
            result (dict): Raw response JSON.

        Returns:
            str: Extracted and cleaned text content.
        """
        if isinstance(result, dict):
            if "message" in result and "content" in result["message"]:
                output = result["message"]["content"]
            elif "response" in result:
                output = result["response"]
            elif "error" in result:
                logger.error(f"LLM Server Error: {result['error']}")
                raise RuntimeError(f"LLM Server Error: {result['error']}")
            else:
                logger.error(f"Unexpected response structure: {result}")
                raise ValueError("Unexpected response structure from LLM server")
        else:
            raise ValueError("Malformed LLM response")

        return self._strip_response(output)

    def _strip_response(self, response: str) -> str:
        """
        Private helper to remove any <think>...</think> tags and trailing whitespace.

        Args:
            response (str): Raw LLM output text.

        Returns:
            str: Cleaned text without think tags.
        """
        return re.sub(r"(?s)^.*?</think>\s*", "", response).strip()
