# modules/llm_loader.py
from config import USE_LOCAL_OLLAMA, OLLAMA_BASE

if USE_LOCAL_OLLAMA:
    from langchain_ollama import OllamaLLM as LLM
else:
    # Placeholder: create this if using ModelArts or another cloud LLM
    from modules.llm_modelarts import ModelArtsLLM as LLM

def get_llm(model_name):
    if USE_LOCAL_OLLAMA:
        return LLM(model=model_name, base_url=OLLAMA_BASE)
    else:
        return LLM(endpoint_name=model_name)
