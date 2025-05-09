"""
reranker.py

Applies reranking to search results using a FlashRank model based on query relevance.

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

logger = logging.getLogger(__name__)

# --------------------------------------------------------
# Reranker
# --------------------------------------------------------

class Reranker:
    """
    Reranker applies a learned ranking model to reorder search results 
    based on semantic relevance to a given query.
    """

    def __init__(self):
        self.env = config.env

        try:
            self.rerank_url = config.ai_models.chatbot.rerank.url
        except AttributeError:
            raise ValueError("Reranker model url missing in config")

        logger.info(f"Loading reranking model from: {self.rerank_url}")

    def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        """
        Rerank a list of documents based on their relevance to the input query.

        Args:
            query (str): The user query.
            documents (list[dict]): List of documents containing 'combined_text'.
            top_k (int, optional): Number of top documents to return. Defaults to 3.

        Returns:
            list[dict]: Top reranked documents sorted by rerank score.
        """
        if not documents:
            logger.warning("No documents provided to rerank.")
            return []

        try:
            logger.info(f"Attempting to score documents...")
            payload = {"text": query, "documents": documents}
            response = requests.post(self.rerank_url, json=payload)
            response.raise_for_status()
            scored_docs = response.json().get("rerank", [])

        except Exception as e:
            logger.error(f"Translation to English failed: {str(e)}")
            return "[Translation Error] Unable to translate to English."
        
        if not scored_docs:
            logger.warning("All documents have empty 'combined_text' or failed scoring.")
            return []

        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        logger.debug(f"Reranked and selected top {top_k} documents.")

        return scored_docs[:top_k]

