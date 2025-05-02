# from flashrank import Ranker

# class FlashRankReranker:
#     def __init__(self, model_name="ms-marco-MiniLM-L-12-v2"):
#         self.ranker = Ranker(model_name)

#     def rerank(self, query: str, documents: list, top_k: int = 3) -> list:
#         if not documents:
#             return []

#         # FlashRank expects {"text": document_text} list
#         docs = [{"text": doc["combined_text"]} for doc in documents]
#         scores = self.ranker.score(query, docs)

#         scored_docs = []
#         for doc, score in zip(documents, scores):
#             scored_docs.append({
#                 "id": doc["id"],
#                 "original_score": doc["score"],
#                 "rerank_score": score,
#                 "combined_text": doc["combined_text"]
#             })

#         # Sort by rerank_score descending
#         scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)

#         return scored_docs[:top_k]
