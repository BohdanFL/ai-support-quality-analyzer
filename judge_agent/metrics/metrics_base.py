from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel

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
        pass