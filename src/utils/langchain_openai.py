import os
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from threading import Lock
from dotenv import load_dotenv
from typing import Optional, List, Any, Dict

load_dotenv('./env/.env.local')

class StreamingCallbackHandler(StreamingStdOutCallbackHandler):
    """
    Custom streaming callback handler with enhanced functionality.
    """
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Run when LLM starts running."""
        super().on_llm_start(serialized, prompts, **kwargs)
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        super().on_llm_new_token(token, **kwargs)
    
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        super().on_llm_end(response, **kwargs)

class OpenAILLM:
    """
    Singleton class to manage ChatOpenAI instances with async streaming support.
    """
    _instance = None
    _lock = Lock()
    _llm_instances = {}

    def __new__(cls, model_name: str = "gpt-4o-mini", temperature: float = 0, streaming: bool = True, callbacks: Optional[List] = None):
        config_key = f"{model_name}_{temperature}_{streaming}_{hash(str(callbacks))}"
        
        if config_key not in cls._llm_instances:
            with cls._lock:
                if config_key not in cls._llm_instances:
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        raise ValueError("OPENAI_API_KEY is not set in environment variables")

                    instance = super(OpenAILLM, cls).__new__(cls)
                    
                    # Set up callbacks for streaming
                    final_callbacks = callbacks
                    if streaming and final_callbacks is None:
                        final_callbacks = [StreamingCallbackHandler()]
                    elif streaming and final_callbacks is not None:
                        has_streaming_callback = any(
                            isinstance(cb, StreamingStdOutCallbackHandler) for cb in final_callbacks
                        )
                        if not has_streaming_callback:
                            final_callbacks.append(StreamingCallbackHandler())
                    
                    # Initialize the LLM
                    instance.llm = ChatOpenAI(
                        model=model_name,
                        temperature=temperature,
                        streaming=streaming,
                        callbacks=final_callbacks,
                        api_key=api_key
                    )
                    
                    instance.config = {
                        "model_name": model_name,
                        "temperature": temperature,
                        "streaming": streaming,
                        "callbacks": final_callbacks
                    }
                    
                    cls._llm_instances[config_key] = instance
        
        return cls._llm_instances[config_key]

    def get_llm(self, streaming: Optional[bool] = None, callbacks: Optional[List] = None) -> ChatOpenAI:
        """Get LLM instance with optional overrides"""
        if streaming is not None or callbacks is not None:
            config = self.config.copy()
            if streaming is not None:
                config["streaming"] = streaming
            if callbacks is not None:
                config["callbacks"] = callbacks
            
            return self._create_llm_instance(**config)
        
        return self.llm

    def get_streaming_llm(self, callbacks: Optional[List] = None) -> ChatOpenAI:
        """Get streaming-configured LLM instance"""
        if callbacks is None:
            callbacks = [StreamingCallbackHandler()]
        else:
            has_streaming_callback = any(
                isinstance(cb, StreamingStdOutCallbackHandler) for cb in callbacks
            )
            if not has_streaming_callback:
                callbacks.append(StreamingCallbackHandler())
        
        return self.get_llm(streaming=True, callbacks=callbacks)

    def get_non_streaming_llm(self) -> ChatOpenAI:
        """Get non-streaming LLM instance"""
        return self.get_llm(streaming=False, callbacks=[])

    def _create_llm_instance(self, model_name: str, temperature: float, streaming: bool, callbacks: List) -> ChatOpenAI:
        """Create new LLM instance"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks,
            api_key=api_key
        )