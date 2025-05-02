import os
import requests

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

SENTENCE_MODEL_PATH = os.getenv("SENTENCE_MODEL_PATH")
CSS_ENDPOINT = os.getenv("CSS_ENDPOINT")

class ChatbotIndexer:
    def __init__(self):
        self.embedder = SentenceTransformer(SENTENCE_MODEL_PATH)
        self.css_endpoint = CSS_ENDPOINT.rstrip('/')

    def query(self, query: str, k: int = 3) -> str:
        embedding = self.embedder.encode(query).tolist()

        payload = {
            "size": k,
            "knn": {
                "field": "embedding",
                "query_vector": embedding,
                "k": k,
                "num_candidates": 100
            }
        }

        try:
            index_name = "issues"
            url = f"{self.css_endpoint}/{index_name}/_search"
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, headers=headers, json=payload, verify=False)
            response.raise_for_status()

            hits = response.json().get("hits", {}).get("hits", [])
            if not hits:
                return "[CSS] No similar issues found."

            results = sorted(hits, key=lambda x: x["_score"], reverse=True)

            final_texts = []
            for hit in results:
                source = hit.get("_source", {})
                combined = source.get("combined_text", "[Missing text]")
                truncated = combined[:2000]  # Limit per document if needed
                score = hit.get("_score", 0.0)
                final_texts.append(f"[Score: {score:.2f}]\n{truncated}")

            return {
                "documents": final_texts,
                "raw_hits": hits,
            }

        except Exception as e:
            return f"[CSS Error] {str(e)}"
