import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any, Type
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

# Configure locking to avoid overwhelming logs
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    # Subclasses must initialize self.client and optionally self.model_name
    
    def _get_generation_kwargs(self) -> dict:
        """Override to provide provider-specific parameters like temperature."""
        return {}

    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_model: Optional[Type[BaseModel]] = None) -> Any:
        """Generate a response from the LLM, optionally returning a validated structured model."""
        
        # Prepare messages once to avoid duplication during retries
        messages = []
        is_gemma = hasattr(self, "model_name") and "gemma" in self.model_name.lower()

        current_prompt = prompt
        if system_prompt:
            if is_gemma:
                current_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": current_prompt})
        kwargs = self._get_generation_kwargs()

        # Inner function to be wrapped by tenacity
        @retry(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        def _execute_generation():
            if response_model:
                return self.client.chat.completions.create(
                    messages=messages,
                    response_model=response_model,
                    **kwargs
                )
            else:
                if "model" not in kwargs and hasattr(self, "model_name"):
                    kwargs["model"] = self.model_name
                
                client_to_use = getattr(self.client, "client", self.client)
                
                if self.name() == "gemini":
                    # Specific handling for GenAi Client text generation
                    response = client_to_use.models.generate_content(
                        model=kwargs["model"],
                        contents=current_prompt,
                        config=kwargs.get("config")
                    )
                    return response.text
                
                response = client_to_use.chat.completions.create(
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content

        try:
            return _execute_generation()
        except Exception as e:
            error_msg = str(e)
            # Log failure after all retries
            logger.error(f"Final generation failure for {self.name()}: {error_msg}")
            
            if response_model:
                raise e
            return f"Error connecting to {self.name()} after retries: {error_msg}"

    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
