import ollama
from typing import Optional, Any
from providers.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "gemma3:1b", host: str = "http://ollama:11434"):
        self.model_name = model_name
        self.client = ollama.Client(host=host)

    def generate(self, prompt: str, system_prompt: Optional[str] = None,response_schema: Optional[Any] = None) -> str:
        format_param = None
        if response_schema:
            # Use Pydantic's JSON schema feature to guide Ollama
            if hasattr(response_schema, "model_json_schema"):
                format_param = response_schema.model_json_schema()
            else:
                format_param = "json"

        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                system=system_prompt,
                format=format_param,
                options={'temperature': 0.2},
                stream=False
            )
            return response.get("response", "")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def name(self) -> str:
        return "ollama"
