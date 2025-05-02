from modules.llm_loader import LLMLoader
from langchain.prompts import PromptTemplate
import textwrap

class QueryModel:
    def __init__(self):
        self.llm = LLMLoader()

        self.general_prompt = PromptTemplate(
            input_variables=["question"],
            template=textwrap.dedent("""\
                You are a helpful municipal assistant in Singapore. Answer the user's question accurately and concisely.

                User question: {question}
                Answer:""")
        )

        self.data_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=textwrap.dedent("""\
                You are a helpful municipal assistant in Singapore. Use the data below to answer the user's question accurately and concisely.

                Context:
                {context}

                User question: {question}
                Answer:""") 
        )

    def ask(self, query_or_messages, context=None, is_follow_up=False):
        """
        Accepts either a string question or a list of chat messages, and sends them
        to the LLM server via LLMLoader.generate().
        """
        if isinstance(query_or_messages, str):
            # Old string-based call, fallback (not preferred)
            if context:
                prompt = self.data_prompt.format(context=context, question=query_or_messages)
            else:
                prompt = self.general_prompt.format(question=query_or_messages)
            return self.llm.generate(prompt, task="query")

        # Chat-based message format
        messages = query_or_messages.copy()

        # Construct or update the system message
        base_prompt = "You are a helpful municipal assistant in Singapore."
        if is_follow_up:
            base_prompt += " The user is continuing from a previous question. Use prior turns to improve your response."

        if context:
            base_prompt += "\n\nUse the following context to help answer the user's query:\n" + context.strip()

        # Check if the first message is a system prompt
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = base_prompt
        else:
            messages.insert(0, {"role": "system", "content": base_prompt})

        return self.llm.generate(messages, task="query")


