import requests
from typing import Optional, Any
from providers.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "gemma3:1b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"

    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_schema: Optional[Any] = None) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        if response_schema:
            payload["format"] = "json"

        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def name(self) -> str:
        return "ollama"
