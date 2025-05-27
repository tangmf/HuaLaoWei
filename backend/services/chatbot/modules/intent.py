"""
intent.py

A core module for the HuaLaoWei municipal chatbot.
Routes user inputs to intents, checks if queries are in municipal scope,
and detects follow-up clarifications based on chat history.

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import re
import difflib
import textwrap
from langchain_core.prompts import PromptTemplate
from backend.services.chatbot.modules.ollama_loader import OllamaLoader

# --------------------------------------------------------
# IntentRouter
# --------------------------------------------------------

class IntentRouter:
    """
    IntentRouter handles intent classification, scope checking,
    and follow-up detection for municipal chatbot queries.
    """

    def __init__(self):
        self.llm = OllamaLoader()

        self.KNOWN_INTENTS = [
            "start_report",
            "check_report_status",
            "data_driven_query",
            "general_query"
        ]

        # Scope checking prompt
        self.scope_prompt = PromptTemplate(
            input_variables=["query"],
            template=textwrap.dedent("""\
                You are a municipal assistant that ONLY has knowledge about municipal or civic services in Singapore, such as:

                - Filing a municipal report (e.g. trash, noise, pests, illegal dumping)
                - Asking about current road conditions, construction, or blockages
                - Questions about local agencies like NEA, LTA, or HDB or town councils like Ang Mo Kio Town Council
                - General inquiries about what kinds of issues different agencies and town councils handle

                You DO NOT answer personal, emotional, nonsensical, or unrelated questions (e.g., about relationships, food, celebrities, hobbies, or general opinions). 
                For those, respond with "NO".

                Only respond with one word: YES or NO.

                Examples:

                Question: Can I file a report about overflowing bins at the park?  
                Answer: YES

                Question: Are there any ongoing road works in Clementi?  
                Answer: YES

                Question: Why do girls keep dumping me? Is it because I make too much noise?  
                Answer: NO

                Question: Do you like durians?  
                Answer: NO

                Question: What does NEA handle?  
                Answer: YES

                Question: How do I report a noise complaint?  
                Answer: YES

                Question: Who's the most handsome actor in Singapore?  
                Answer: NO

                ---

                Now classify the following, and remember your response is STRICTLY either "YES" or "NO":

                Question: {query}  
                Answer:
            """)
        )

        # Intent classification prompt
        self.intent_prompt = PromptTemplate(
            input_variables=["query"],
            template=textwrap.dedent("""\
                You are a municipal assistant. Classify the user municipal-related query into one of these intent types:
                                     
                1. START_REPORT - When the user wants to start a new issue report.
                2. CHECK_REPORT_STATUS - When the user wants to check or enquire about an EXISTING report they already submitted.
                3. DATA_DRIVEN_QUERY - When the user needs real-time or live data (e.g., road closures, dengue hotspots).
                4. GENERAL_QUERY - When the user asks broad municipal questions (e.g., about NEA, LTA, agencies).

                Respond with only the intent type.

                Examples:

                Query: Can I report illegal dumping here?  
                Answer: START_REPORT
                                     
                Query: Has my noise complaint been processed?
                Answer: CHECK_REPORT_STATUS

                Query: Are there any blockages near Clementi today?  
                Answer: DATA_DRIVEN_QUERY

                Query: What types of cases does NEA handle?  
                Answer: GENERAL_QUERY

                Query: There’s a lot of trash near the void deck, how do I report it?  
                Answer: START_REPORT
                                     
                Query: I've reported an issue about a broken traffic light ages ago, why has it not been fixed yet?
                Answer: CHECK_REPORT_STATUS

                Query: Are there any dengue hotspots this week?  
                Answer: DATA_DRIVEN_QUERY

                Query: What does LTA do?  
                Answer: GENERAL_QUERY

                ---

                Now classify:

                Query: {query}  
                Answer:
            """)
        )

        # Follow-up detection prompt (system role)
        self.followup_prompt = {
            "role": "system",
            "content": textwrap.dedent("""\
                You are a municipal assistant. A user and another chatbot had a conversation relating to the municipal topic.
                Based on the chat history, determine if the LAST user message is a FOLLOW-UP or CLARIFICATION to the earlier conversation. 
                A follow-up continues the current topic or asks for more detail on a specific point the chatbot replied with. 
                                       
                Respond strictly with YES or NO.

                Examples:

                Example 1:
                User: Is there a road blockage near Bukit Timah?
                Chatbot: Yes, there was a report made on 2025-10-01 about a highly severe blockage on Bukit Timah Road with a fallen tree.
                User: What's the status of that report?
                Answer: YES

                Example 2:
                User: What does NEA do?
                Assistant: NEA handles environmental services like waste and pest control.
                User: By the way, who's the Prime Minister of Singapore?
                Answer: NO

                Example 3:
                User: Can I report noise complaints here?
                Assistant: Yes, you can report them through this chatbot.
                User: Yes I would like to file one now
                Answer: YES

                Example 4:
                User: Is this chatbot trained on Singapore laws?
                Assistant: I can help with Singapore municipal topics and services.
                User: What does that mean?
                Answer: YES

                Now evaluate the following chat history:
            """)
        }
    
    # --------------------------------------------------------
    # Public Methods
    # --------------------------------------------------------

    def is_in_scope(self, query: str) -> bool:
        """
        Determine if the query is within municipal service topics.

        Args:
            query (str): User query.

        Returns:
            bool: True if in scope, False otherwise.
        """
        try:
            result = self.llm.generate(self.scope_prompt.format(query=query), task="intent")
            return "yes" in result.strip().lower()
        except Exception:
            return False

    def classify_intent(self, query: str) -> str:
        """
        Classify the intent of the user query.

        Args:
            query (str): User query.

        Returns:
            str: Predicted intent type.
        """
        try:
            raw_intent = self.llm.generate(self.intent_prompt.format(query=query), task="intent").strip()
            canonical_intent = self._canonicalize(raw_intent)
            matched_intent = self._match_intent(canonical_intent)
            return matched_intent
        except Exception:
            return "general_query"

    def is_follow_up(self, chat_messages: list) -> bool:
        """
        Check whether the latest user message is a follow-up or clarification.

        Args:
            chat_messages (list): Structured chat history.

        Returns:
            bool: True if last user message is a follow-up, False otherwise.
        """
        if not chat_messages or chat_messages[-1]["role"] != "user":
            return False

        history = chat_messages[-5:]  # Only consider last 5 messages

        try:
            response = self.llm.generate([
                self.followup_prompt,
                *history,
                {"role": "user", "content": "Is the last user message a follow-up? Answer:"}
            ], task="followup_check").strip().lower()
            return "yes" in response
        except Exception:
            return False
    
    # --------------------------------------------------------
    # Private Helper Methods
    # --------------------------------------------------------

    def _canonicalize(self, text: str) -> str:
        """
        Canonicalize text into snake_case for easier matching.

        Args:
            text (str): Input text.

        Returns:
            str: Snake_case normalized text.
        """
        if not isinstance(text, str):
            return ""

        text = text.strip()
        if "_" in text or "-" in text or " " in text:
            words = re.split(r"[_\-\s]+", text)
        else:
            words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", text)

        return "_".join(word.lower() for word in words if word).strip("_")

    def _match_intent(self, normalized: str) -> str:
        """
        Match a predicted intent to the closest known intent.

        Args:
            intent (str): Predicted intent.

        Returns:
            str: Best matched known intent or None.
        """
        for known in self.KNOWN_INTENTS:
            if known in normalized:
                return known

        best = difflib.get_close_matches(normalized, self.KNOWN_INTENTS, n=1, cutoff=0.75)
        return best[0] if best else "general_query"
