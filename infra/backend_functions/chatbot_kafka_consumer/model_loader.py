from sentence_transformers import SentenceTransformer

def load_embedder():
    return SentenceTransformer("./models/sentence_model", local_files_only=True)