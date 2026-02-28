import json
from typing import Dict, Any
from providers.base import LLMProvider
from providers.gemini import GeminiProvider
from pathlib import Path
from judge_agent.models import SupportEvaluationResult
from pydantic import ValidationError

class LLMJudge:

    @property
    def prompt_filename(self) -> str:
        return "support_quality_metric_prompt.md"
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def get_analysis_prompt(self, dialogue: str):
        prompt = Path(f"prompts/{self.prompt_filename}").read_text(encoding="utf-8")
        return prompt.format(dialogue=dialogue)
    
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

    def evaluate_dialogue(self, dialogue: str) -> Dict[str, Any]:
        evaluation_results = {}
        prompt = self.get_analysis_prompt(dialogue)
            
        raw_response = self.provider.generate(
            prompt=prompt,
            system_prompt="You are an AI assistant tasked with evaluating dialogues strictly following the schema.",
            response_model=SupportEvaluationResult
        )

        result = self.parse_response(raw_response)
        evaluation_results["result"] = result
            
        return evaluation_results