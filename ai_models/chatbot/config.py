import os

ENV = os.getenv("ENV", "dev")  # dev (local Docker), test (Huawei ECS)

USE_LOCAL_MODELS = ENV == "dev"
USE_LOCAL_OLLAMA = ENV == "dev"

MODEL_PATHS = {
    "whisper": "./models/whisper_tiny" if USE_LOCAL_MODELS else "/mnt/models/whisper_tiny",
    "nllb": "./models/nllb_model" if USE_LOCAL_MODELS else "/mnt/models/nllb_model",
    "sentence_model": "./models/sentence_model" if USE_LOCAL_MODELS else "/mnt/models/sentence_model",
}

CHROMA_PATH = "./vector_stores/chroma_store_textonly" if USE_LOCAL_MODELS else "/mnt/vector_store"
OLLAMA_BASE = (
    os.getenv("OLLAMA_API_BASE")
    or ("http://ollama:11434" if USE_LOCAL_OLLAMA else "http://<your-ecs-ip>:11434")
)
