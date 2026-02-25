import ollama
from typing import Optional, Any
from providers.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "gemma3:1b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.client = ollama.Client(host=host)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_schema: Optional[Any] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        format_param = None
        if response_schema:
            try:
                # Use Pydantic's JSON schema for Ollama's format parameter
                format_param = response_schema.model_json_schema()
            except AttributeError:
                format_param = "json"

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                format=format_param,
                stream=False,
                options={'temperature': 0}
            )
            return response.message.content
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def name(self) -> str:
        return "ollama"
