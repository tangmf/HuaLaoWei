# modules/query_model.py

import re
import time
import httpx
import textwrap
from config import OLLAMA_BASE, USE_LOCAL_OLLAMA
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

def wait_for_ollama_model_ready(base_url: str, model: str, timeout: int = 2000):
    print(f"Waiting for Ollama model '{model}' to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = httpx.get(f"{base_url}/api/tags")
            if r.status_code == 200 and any(m["name"].startswith(model) for m in r.json().get("models", [])):
                print(f"Model '{model}' is ready.")
                return
        except Exception as e:
            print(f"Waiting... ({e})")
        time.sleep(3)

    raise TimeoutError(f"Ollama model '{model}' was not ready within {timeout} seconds.")

class QueryModel:
    def __init__(self):
        self.model_name = "deepseek-r1:7b"
        if USE_LOCAL_OLLAMA:
            wait_for_ollama_model_ready(base_url=OLLAMA_BASE, model=self.model_name)
            print(f"Using Deepseek model via Ollama at: {OLLAMA_BASE}")
            self.llm = OllamaLLM(model=self.model_name, base_url=OLLAMA_BASE)
        else:
            raise NotImplementedError("Cloud-based DeepSeek querying not yet supported")
        
        # For GENERAL_QUERY
        self.general_prompt = PromptTemplate(
            input_variables=["question"],
            template=textwrap.dedent("""\
                You are a helpful municipal assistant in Singapore. Answer the user's question accurately and concisely.
                                     
                User question: {question}
                Answer:""")
        )
        
        # For DATA_DRIVEN_QUERY
        self.data_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=textwrap.dedent("""\
                You are a helpful municipal assistant in Singapore. Use the data below to answer the user's question accurately and concisely.

                Context:
                {context}

                User question: {question}
                Answer:""")
        )

    @staticmethod
    def split_thought_and_answer(llm_output: str):
        match = re.search(r"<think>(.*?)</think>(.*)", llm_output, re.DOTALL)
        if match:
            thought = match.group(1).strip()
            answer = match.group(2).strip()
            return thought, answer
        else:
            return None, llm_output.strip()

    def ask(self, query, context=None):
        if context:
            chain = self.data_prompt | self.llm
            response = chain.invoke({"context": context, "question": query})
        else:
            chain = self.general_prompt | self.llm
            response = chain.invoke({"question": query})

        # Only if you're using deepseek-r1
        if "deepseek" in self.model_name:
            thought, answer = self.split_thought_and_answer(response)
            return answer
        
        return response