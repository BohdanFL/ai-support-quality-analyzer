from abc import ABC, abstractmethod
from typing import Optional, Any, Type
from pydantic import BaseModel

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    # Subclasses must initialize self.client and optionally self.model_name
    
    def _get_generation_kwargs(self) -> dict:
        """Override to provide provider-specific parameters like temperature."""
        return {}
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[BaseModel]] = None) -> Any:
        """Generate a response from the LLM, optionally returning a validated structured model."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = self._get_generation_kwargs()

        try:
            if response_model:
                return self.client.chat.completions.create(
                    messages=messages,
                    response_model=response_model,
                    **kwargs
                )
            else:
                response = self.client.chat.completions.create(
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
        except Exception as e:
            if response_model:
                raise e
            return f"Error connecting to {self.name()}: {str(e)}"

    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
