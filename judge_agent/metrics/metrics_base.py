from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Metric(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def response_schema(self) -> Optional[Dict[str, Any]]:
        return None

    @abstractmethod
    def build_prompt(self, dialogue: str) -> str:
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        pass