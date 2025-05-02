import chromadb
from model_loader import load_embedder

client = chromadb.PersistentClient(path="./chroma-data")
collection = client.get_or_create_collection("municipal_issues")
embedder = load_embedder()

def upsert_to_chroma(doc_id, content, metadata):
    embedding = embedder.encode(content).tolist()
    collection.upsert(documents=[content], embeddings=[embedding], ids=[doc_id], metadatas=[metadata])