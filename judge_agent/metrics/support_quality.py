from typing import Dict, Any, Optional
from pydantic import ValidationError
from judge_agent.models import SupportEvaluationResult
from judge_agent.metrics.metrics_base import Metric
import json
from pathlib import Path


class SupportQualityMetric(Metric):
    @property
    def prompt_filename(self) -> str:
        return "support_quality_metric_prompt.md"

    @property
    def name(self) -> str:
        return "support_quality_analysis"

    @property
    def response_schema(self) -> Optional[Dict[str, Any]]:
        return SupportEvaluationResult.model_json_schema()

    def build_prompt(self, dialogue: str) -> str:
        prompt = Path(f"prompts/{self.prompt_filename}").read_text(encoding="utf-8")
        return prompt.format(dialogue=dialogue)

    def parse_response(self, response: str) -> Dict[str, Any]:
        try:
            clean_response = response.strip().strip("`").removeprefix("json").strip()
            
            raw_dict = json.loads(clean_response)
            
            validated_data = SupportEvaluationResult(**raw_dict)
            return validated_data.model_dump()
            
        except (json.JSONDecodeError, ValidationError) as e:
            return {
                "error": "Failed to parse or validate LLM response",
                "details": str(e),
                "raw_response": response
            }