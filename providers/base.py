from abc import ABC, abstractmethod
from typing import Optional, Any

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_schema: Optional[Any] = None) -> str:
        """Generate a response from the LLM, optionally with a schema."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
