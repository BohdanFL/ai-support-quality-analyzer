import json
from typing import List, Dict, Any
from judge_agent.metrics.metrics_base import Metric
from judge_agent.metrics.support_quality import SupportQualityMetric
from providers.base import LLMProvider
from providers.gemini import GeminiProvider

class LLMJudge:
    def __init__(self, provider: LLMProvider, metrics: List[Metric]):
        self.provider = provider
        self.metrics = metrics

    def evaluate_dialogue(self, dialogue: str) -> Dict[str, Any]:
        evaluation_results = {}
        for metric in self.metrics:
            prompt = metric.build_prompt(dialogue)
            
            raw_response = self.provider.generate(
                prompt=prompt,
                system_prompt="You are an AI assistant tasked with evaluating dialogues strictly following the schema.",
                response_model=metric.response_model
            )
            result = metric.parse_response(raw_response)
            evaluation_results[metric.name] = result
            
        return evaluation_results

if __name__ == "__main__":
    sample_dialogue = """
    Клієнт: Привіт! Я вчора скасував підписку, але гроші все одно зняло. Коли буде повернення?
    Агент: Вітаю! Ваша підписка вже скасована. Гарного дня!
    Клієнт: Але ж ви зняли гроші! Коли вони повернуться на картку??
    Агент: Підписка не активна. До побачення.
    """

    provider = GeminiProvider()

    metrics = [SupportQualityMetric()]
    judge = LLMJudge(provider=provider, metrics=metrics)

    result = judge.evaluate_dialogue(sample_dialogue)
    
    print(json.dumps(result, indent=4, ensure_ascii=False))