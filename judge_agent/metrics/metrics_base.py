from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import ValidationError, BaseModel
from judge_agent.models import SupportEvaluationResult
import json

class Metric(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def response_model(self) -> Optional[Type[BaseModel]]:
        return None

    @abstractmethod
    def build_prompt(self, dialogue: str) -> str:
        pass

    @abstractmethod
    def parse_response(self, response: Any) -> Dict[str, Any]:
        try:
            if isinstance(response, SupportEvaluationResult):
                return response.model_dump()

            return {
                "error": "Failed to receive a valid response object",
                "raw_response": str(response)
            }

        except ValidationError as e:
            return {
                "error": "Failed to parse or validate LLM response",
                "details": str(e)
            }