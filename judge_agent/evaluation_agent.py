import json
from typing import List, Dict, Any
from judge_agent.metrics.metrics_base import Metric
from judge_agent.metrics.support_quality import SupportQualityMetric
from providers.base import LLMProvider
from providers.gemini import GeminiProvider
from pathlib import Path

class LLMJudge:
    def __init__(self, provider: LLMProvider, metrics: List[Metric]):
        self.provider = provider
        self.metrics = metrics

    def evaluate_dialogue(self, dialogue: str) -> Dict[str, Any]:
        evaluation_results = {}
        for metric in self.metrics:
            prompt = metric.build_prompt(dialogue)
            print("Sending prompt:")
            print(prompt)
            print("\nSending to LLM...")
            llm_response = self.provider.generate(prompt, response_schema=metric.response_schema)
            print("LLM response:")
            print(llm_response)
            print("END")
            result = metric.parse_response(llm_response)
            evaluation_results[metric.name] = result
            
        return evaluation_results

if __name__ == "__main__":
    prompt_filename = "./prompts/sample_dialogue.md"

    sample_dialogue = Path(f"prompts/{prompt_filename}").read_text(encoding="utf-8")

    provider = GeminiProvider()

    metrics = [SupportQualityMetric()]
    judge = LLMJudge(provider=provider, metrics=metrics)

    result = judge.evaluate_dialogue(sample_dialogue)
    
    print(json.dumps(result, indent=4, ensure_ascii=False))