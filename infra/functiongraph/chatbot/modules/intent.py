from langchain_core.prompts import PromptTemplate
from modules.llm_loader import LLMLoader
import textwrap

class IntentRouter:
    def __init__(self):
        self.llm = LLMLoader()
        self.scope_prompt = PromptTemplate(
            input_variables=["query"],
            template="""You are a municipal assistant who ONLY answers questions about municipal or civic services in Singapore, such as:

- Filing a municipal report (e.g. trash, noise, pests, illegal dumping)
- Asking about current road conditions, construction, or blockages
- Questions about local agencies like NEA, LTA, or HDB or town councils like Ang Mo Kio Town Council
- General inquiries about what kinds of issues different agencies and town councils handle

You DO NOT answer personal, emotional, nonsensical, or unrelated questions (e.g. about relationships, food, celebrities, hobbies, or general opinions). For those, respond with "NO".

Only respond with one word: YES or NO.

### Examples:

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
Answer:"""
        )

        self.intent_prompt = PromptTemplate(
            input_variables=["query"],
            template="""
You are a municipal assistant. Classify the user municipal-related query into one of these intent types:

1. NARROW_INTENT – Specific phrases or flows. Usually for filing a report or checking the status of their report.
2. DATA_DRIVEN_QUERY – Needs real-time or live data to answer (e.g., road blockages, weather).
3. GENERAL_QUERY – Broad municipal questions based on general or historical info (e.g., agency roles).

Respond with only the intent type.

### Examples:

Query: Can I report illegal dumping here?  
Answer: NARROW_INTENT

Query: Are there any blockages near Clementi today?  
Answer: DATA_DRIVEN_QUERY

Query: What types of cases does NEA handle?  
Answer: GENERAL_QUERY

Query: There’s a lot of trash near the void deck, how do I report it?  
Answer: NARROW_INTENT

Query: Are there any dengue hotspots this week?  
Answer: DATA_DRIVEN_QUERY

Query: What does LTA do?  
Answer: GENERAL_QUERY

---

Now classify:

Query: {query}  
Answer:
"""
        )

    def is_in_scope(self, query):
        result = self.llm.generate(self.scope_prompt.format(query=query), task="intent")
        return "yes" in result.strip().lower()

    def classify_intent(self, query):
        return self.llm.generate(self.intent_prompt.format(query=query), task="intent").strip()


    def is_follow_up(self, chat_messages):
        """
        Determine if the latest user message is a follow-up or clarification,
        using few-shot prompting with the last 4–5 message turns.
        """
        if not chat_messages or chat_messages[-1]["role"] != "user":
            return False

        history = chat_messages[-5:]  # Keep last 5 turns to conserve tokens

        followup_intro = {
            "role": "system",
            "content": textwrap.dedent("""\
                You are a helpful assistant. Based on the chat history, determine if the LAST user message is a FOLLOW-UP or CLARIFICATION
                to the earlier conversation. A follow-up continues the current topic or asks for more detail. Respond strictly with YES or NO.

                Examples:

                Example 1:
                User: How do I report illegal dumping?
                Assistant: You can report it via the OneService app or your Town Council.
                User: How long does it take to process?
                Answer: YES

                Example 2:
                User: What does NEA do?
                Assistant: NEA handles environmental services like waste and pest control.
                User: By the way, who's the Prime Minister of Singapore?
                Answer: NO

                Example 3:
                User: Can I report noise complaints here?
                Assistant: Yes, you can report them through this chatbot or the OneService app.
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

        prompt = [
            followup_intro,
            *history,
            {"role": "user", "content": "Is the last user message a follow-up? Answer:"}
        ]

        try:
            response = self.llm.generate(prompt, task="followup_check").strip().lower()
            return "yes" in response
        except Exception as e:
            return False