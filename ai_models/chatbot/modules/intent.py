# modules/intent.py

import time
import httpx
from modules.llm_loader import get_llm
from config import USE_LOCAL_OLLAMA, OLLAMA_BASE

from langchain_core.prompts import PromptTemplate

def wait_for_ollama_model_ready(base_url: str, model: str, timeout: int = 2000):
    print(f"Waiting for Ollama model '{model}' to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = httpx.get(f"{base_url}/api/tags")
            if r.status_code == 200 and any(m["name"].startswith(model) for m in r.json().get("models", [])):
                print(f"Model '{model}' is ready.")
                return
        except Exception as e:
            print(f"Waiting... ({e})")
        time.sleep(3)

    raise TimeoutError(f"Ollama model '{model}' was not ready within {timeout} seconds.")


class IntentRouter:
    def __init__(self):
        self.model_name = "mistral:7b"

        if USE_LOCAL_OLLAMA:
            wait_for_ollama_model_ready(base_url=OLLAMA_BASE, model=self.model_name)

        self.llm = get_llm(self.model_name)

        self.scope_prompt = PromptTemplate(
            input_variables=["query"],
            template="""
You are a municipal assistant who ONLY answers questions about municipal or civic services in Singapore, such as:

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
Answer:
"""
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

        self.scope_chain = self.scope_prompt | self.llm
        self.intent_chain = self.intent_prompt | self.llm

    def is_in_scope(self, query):
        return "yes" in self.scope_chain.invoke({"query": query}).strip().lower()

    def classify_intent(self, query):
        return self.intent_chain.invoke({"query": query}).strip()
