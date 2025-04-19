# modules/llm_modelarts.py

import requests

class ModelArtsLLM:
    def __init__(self, endpoint_name):
        self.endpoint = f"https://<your_modelarts_endpoint_url>/{endpoint_name}"  # Adjust accordingly

    def invoke(self, input_dict):
        # Send a POST request to your ModelArts inference endpoint
        payload = {
            "inputs": input_dict["query"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("result", "No response")
        except Exception as e:
            return f"[ModelArts Error] {str(e)}"
