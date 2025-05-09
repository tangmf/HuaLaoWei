"""
query.py

A core service for the HuaLaoWei municipal chatbot.
Handles structured query submission to the LLM server for municipal question answering.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import textwrap
from ollama_loader import OllamaLoader

# --------------------------------------------------------
# Query Service
# --------------------------------------------------------

class QueryService:
    """
    QueryService formats chat queries and manages interactions with the LLM server
    for municipal assistant-style answers.
    """

    def __init__(self):
        self.llm = OllamaLoader()
        self.base_prompt_content = textwrap.dedent("""\
            You are a municipal assistant in Singapore. Answer the user's questions clearly and concisely.
            When prior conversation history is available, use it to inform your answers, otherwise just answer to the best of your knowledge.
        """)

    def ask(
        self,
        query_or_messages: list[dict],
        context: str = None,
    ) -> str:
        """
        Send a list of chat messages to the LLM server for a final response.

        Args:
            query_or_messages (list[dict]): Chat history including user queries and assistant responses.
            context (str, optional): Additional context to inform the answer. Defaults to None.

        Returns:
            str: Generated response from LLM.
        """
        messages = query_or_messages.copy()
        system_message = self._build_system_prompt(context)

        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = system_message["content"]
        else:
            messages.insert(0, system_message)

        return self.llm.generate(messages, model="deepseek:14b")

    # --------------------------------------------------------
    # Private Helper Methods
    # --------------------------------------------------------

    def _build_system_prompt(self, context: str = None) -> dict:
        """
        Private helper to construct a system prompt, optionally injecting external context.

        Args:
            context (str, optional): Additional context to append.

        Returns:
            dict: Formatted system prompt dictionary.
        """
        prompt_content = self.base_prompt_content

        if context:
            prompt_content += "\n\nUse the following context to help answer the user's query:\n" + context.strip()

        return {"role": "system", "content": prompt_content}
