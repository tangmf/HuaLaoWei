"""
indexer.py

A core module for the HuaLaoWei municipal chatbot.
Handles semantic search queries for the chatbot RAG system using either a 
local ChromaDB instance (development mode) or Huawei Cloud CSS (production mode).

Author: Fleming Siow
Date: 3rd May 2025
"""

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

import logging
import requests
from config.config import config

# --------------------------------------------------------
# Logger Setup
# --------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Chatbot Indexer
# --------------------------------------------------------

class ChatbotIndexer:
    """
    ChatbotIndexer manages semantic search capabilities for the chatbot.

    In development mode, it uses Weaviate for local vector search.
    In production mode, it queries Huawei Cloud CSS for vector search results.
    """

    def __init__(self):
        self.env = config.env
        
        try:
            self.embed_url = config.ai_models.chatbot.embed.url
        except AttributeError:
            raise ValueError("Embedding model url missing in config")

        logger.info(f"Loading sentence embedding model from: {self.embed_url}")

        if self.env == "dev":
            import weaviate
            try:
                self.vectorstore_config = config.data_stores.vectorstore
                self.vectorstore_url = self.vectorstore_config.url
            except AttributeError:
                raise ValueError("Vectorstore url missing in config")
        
            self.client = weaviate.Client(url=self.vectorstore_url)

            try:
                self.collection_name = config.data_stores.vectorstore.collection["issue"].name
            except AttributeError:
                raise ValueError("Vectorstore collection name missing in config")

            if not self.client.schema.exists(self.collection_name):
                raise ValueError(f"Vectorstore collection '{self.collection_name}' not found. Please set up schema.")

            logger.info(f"Using local Weaviate vectorstore {self.collection_name} collection at: {self.vectorstore_url}")

        else:
            try:              
                self.vectorstore_config = config.data_stores.vectorstore
                self.vectorstore_url = self.vectorstore_config.url
            except AttributeError:
                raise ValueError("Vectorstore url missing in config")
            
            try:              
                self.index_name = self.vectorstore_config.index_name
            except AttributeError:
                raise ValueError("Vectorstore index name missing in config")
            

    def query(self, query_text, k=3):
        """
        Perform a semantic search query based on the input text.

        Args:
            query_text (str): The user query to search.
            k (int): The number of top similar results to return.

        Returns:
            dict | str: Search results or error message.
        """
        try:
            logger.info(f"Attempting to generate embedding...")
            payload = {"text": query_text}
            response = requests.post(self.embed_url, json=payload)
            response.raise_for_status()
            embedding = response.json().get("embedding", "")

            embedding = self.embedder.encode(query_text).tolist()
        
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return f"[Embedding Error] {str(e)}"

        if self.env == "dev":
            return self._query_local(embedding, k)
        else:
            return self._query_cloud(embedding, k)

    def _query_local(self, embedding, k):
        """
        Query the local Weaviate instance.
        """
        try:
            logger.info("Querying Weaviate...")
            result = (
                self.client.query
                .get(self.collection_name, ["combined_text", "issue_id", "issue_type", "issue_subtype"])
                .with_near_vector({"vector": embedding})
                .with_limit(k)
                .do()
            )

            docs = result.get("data", {}).get("Get", {}).get(self.collection_name, [])

            if not docs:
                logger.warning("Weaviate returned no similar issues.")
                return "[Weaviate] No similar issues found."

            final_texts = []
            for doc in docs:
                text = doc.get("combined_text", "[Missing text]")[:2000]
                final_texts.append(text)

            return {
                "documents": final_texts,
                "raw_hits": docs,
            }

        except Exception as e:
            logger.error(f"Weaviate query failed: {str(e)}")
            return f"[Weaviate Error] {str(e)}"
        
    def _query_cloud(self, embedding, k):
        """
        Query the Huawei Cloud CSS service.
        """
        logger.info("Querying Huawei Cloud CSS...")
        url = f"{self.vectorstore_url}/{self.index_name}/_search"
        headers = {"Content-Type": "application/json"}

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
            response = requests.post(url, headers=headers, json=payload, verify=False)
            response.raise_for_status()
            hits = response.json().get("hits", {}).get("hits", [])

            if not hits:
                logger.warning("CSS returned no similar issues.")
                return "[CSS] No similar issues found."

            results = sorted(hits, key=lambda x: x.get("_score", 0.0), reverse=True)

            final_texts = []
            for hit in results:
                source = hit.get("_source", {})
                combined = source.get("combined_text", "[Missing text]")
                truncated = combined[:2000]  # Safety limit
                score = hit.get("_score", 0.0)
                final_texts.append(f"[Score: {score:.2f}]\n{truncated}")

            return {
                "documents": final_texts,
                "raw_hits": hits,
            }

        except requests.RequestException as e:
            logger.error(f"Request to CSS failed: {str(e)}")
            return f"[CSS Request Error] {str(e)}"

        except Exception as e:
            logger.error(f"Unexpected error querying CSS: {str(e)}")
            return f"[CSS Error] {str(e)}"