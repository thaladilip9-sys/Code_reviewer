import os
from langchain.chat_models import ChatOpenAI
from threading import Lock

class OpenAILLM:
    """
    Singleton class to manage a single instance of ChatOpenAI for LangChain.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, model_name="gpt-4o-mini", temperature=0, streaming=True):
        if cls._instance is None:
            with cls._lock:  # thread-safe singleton
                if cls._instance is None:
                    # Ensure API key is set
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        raise ValueError("OPENAI_API_KEY is not set in environment variables")

                    cls._instance = super(OpenAILLM, cls).__new__(cls)
                    # Initialize the LLM
                    cls._instance.llm = ChatOpenAI(
                        model_name=model_name,
                        temperature=temperature,
                        streaming=streaming
                    )
        return cls._instance

    def get_llm(self):
        """
        Return the ChatOpenAI instance
        """
        return self.llm
