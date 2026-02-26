import os
from typing import Optional
from providers.base import LLMProvider
from providers.gemini import GeminiProvider
from providers.groq import GroqProvider
from providers.ollama import OllamaProvider
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")

def get_llm_provider(provider_type: str, model_name: Optional[str] = None) -> LLMProvider:
    provider_type = provider_type.lower()
    
    if model_name is None:
        model_name = MODEL_NAME
        
    if provider_type == "gemini":
        return GeminiProvider(model_name=model_name or "gemini-2.5-flash")
    elif provider_type == "groq":
        return GroqProvider(model_name=model_name or "llama-3.3-70b-versatile")
    elif provider_type == "ollama":
        return OllamaProvider(model_name=model_name or "llama2")
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
