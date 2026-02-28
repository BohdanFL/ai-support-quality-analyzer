from typing import Dict, Any, Optional, Type
from judge_agent.models import SupportEvaluationResult
from judge_agent.metrics.metrics_base import Metric
from pydantic import BaseModel
from pathlib import Path


class SupportQualityMetric(Metric):
    @property
    def prompt_filename(self) -> str:
        return "support_quality_metric_prompt.md"

    @property
    def name(self) -> str:
        return "support_quality_analysis"

    @property
    def response_model(self) -> Optional[Type[BaseModel]]:
        return SupportEvaluationResult

    def build_prompt(self, dialogue: str) -> str:
        prompt = Path(f"prompts/{self.prompt_filename}").read_text(encoding="utf-8")
        return prompt.format(dialogue=dialogue)

    def parse_response(self, response: str) -> Dict[str, Any]:
        return super().parse_response(response)