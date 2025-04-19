# modules/indexer.py

from config import ENV, CHROMA_PATH, MODEL_PATHS
from sentence_transformers import SentenceTransformer

if ENV == "dev":
    import chromadb
else:
    import requests  # for Huawei Cloud CSS REST calls

class ChatbotIndexer:
    def __init__(self):
        model_path = MODEL_PATHS["sentence_model"]
        print(f"Loading sentence embedding model from: {model_path}")
        self.embedder = SentenceTransformer(model_path)

        if ENV == "dev":
            print(f"Using ChromaDB at: {CHROMA_PATH}")
            self.client = chromadb.PersistentClient(path=CHROMA_PATH)
            self.collection = self.client.get_or_create_collection("municipal_issues")
            if not self.collection.count():
                print("ChromaDB collection is empty. Consider seeding it.")
        else:
            print("Using Huawei Cloud CSS for semantic search")
            self.css_endpoint = "https://<your-css-endpoint>/v1/indexes/municipal_issues/_search"  # Replace with real
            self.css_auth_token = "<your-auth-token>"  # Ideally load from env or secret

    def query(self, user_query, k=3):
        embedding = self.embedder.encode(user_query).tolist()

        if ENV == "dev":
            print("Querying ChromaDB...")
            results = self.collection.query(query_embeddings=[embedding], n_results=k)
            return results
        else:
            print("Querying Huawei CSS...")
            payload = {
                "size": k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": embedding,
                            "k": k
                        }
                    }
                }
            }
            headers = {
                "Authorization": f"Bearer {self.css_auth_token}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(self.css_endpoint, json=payload, headers=headers)
                response.raise_for_status()
                hits = response.json()["hits"]["hits"]
                return "\n\n".join(hit["_source"]["text"] for hit in hits)
            except Exception as e:
                return f"[CSS Error] {str(e)}"
