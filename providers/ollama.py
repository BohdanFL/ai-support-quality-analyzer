import os
import instructor
from providers.base import LLMProvider
from dotenv import load_dotenv

load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_HOST = os.getenv("OLLAMA_HOST",  "http://localhost:11434")

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        self.model_name = model_name
        self.host = host
        
        # Simple setup using instructor's auto client for Ollama
        self.client = instructor.from_provider(
            f"ollama/{self.model_name}",
            mode=instructor.Mode.JSON,
            base_url=f"{self.host}/v1"
        )

    def _get_generation_kwargs(self) -> dict:
        return {
            "temperature": 0,
            "seed": 42
        }

    def name(self) -> str:
        return "ollama"
