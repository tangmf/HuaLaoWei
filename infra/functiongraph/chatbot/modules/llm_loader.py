import os
import re
import requests

class LLMLoader:
    def __init__(self):
        # Read your LLM API endpoint URL from environment variable
        self.url = os.getenv("LLM_ENDPOINT")
        if not self.url:
            raise EnvironmentError("Environment variable 'LLM_ENDPOINT' is missing.")

        # Read model names from environment variables
        self.intent_model = os.getenv("INTENT_MODEL", "phi")
        self.query_model = os.getenv("QUERY_MODEL", "llama3:8b")

    def strip_think(self, response: str) -> str:
        """
        Removes any LLM inner thoughts (e.g., <think>...</think>) and extra newlines.
        """
        return re.sub(r"(?s)^.*?</think>\s*", "", response).strip()

    def generate(self, prompt_or_messages, task="query"):
        # Select the model
        model = self.intent_model if task == "intent" or task == "followup_check" else self.query_model

        # Case 1: string prompt (old format)
        if isinstance(prompt_or_messages, str):
            payload = {
                "model": model,
                "prompt": prompt_or_messages,
                "stream": False
            }
            endpoint = f"{self.url}/api/generate"

        # Case 2: structured chat messages (new format)
        elif isinstance(prompt_or_messages, list):
            payload = {
                "model": model,
                "messages": prompt_or_messages,
                "stream": False
            }
            endpoint = f"{self.url}/api/chat"

        else:
            raise ValueError("Unsupported prompt format. Must be string or list of chat messages.")

        try:
            response = requests.post(endpoint, json=payload, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to LLM server: {e}")

        result = response.json()

        if isinstance(result, dict) and "message" in result and "content" in result["message"]:
            output = result["message"]["content"]
        elif isinstance(result, dict) and "response" in result:
            output = result["response"]
        elif isinstance(result, dict) and "error" in result:
            raise RuntimeError(f"LLM Server Error: {result['error']}")
        else:
            raise ValueError("Unexpected response structure from LLM server")
        
        # Strip <think> only for relevant tasks
        output = self.strip_think(output)

        return output

