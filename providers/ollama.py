import os
from typing import Optional, Any, Type
from pydantic import BaseModel
import instructor
from providers.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "gemma3:1b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        
        # Simple setup using instructor's auto client for Ollama
        self.client = instructor.from_provider(
            f"ollama/{self.model_name}",
            mode=instructor.Mode.JSON,
            base_url=f"{self.host}/v1"
        )

    def _get_generation_kwargs(self) -> dict:
        return {"temperature": 0.2}

    def name(self) -> str:
        return "ollama"
