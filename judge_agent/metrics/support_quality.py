from typing import Dict, Any, Optional
from pydantic import ValidationError
from judge_agent.models import SupportEvaluationResult
from judge_agent.metrics.metrics_base import Metric
import json


class SupportQualityMetric(Metric):
    @property
    def name(self) -> str:
        return "support_quality_analysis"

    @property
    def response_schema(self) -> Optional[Dict[str, Any]]:
        return SupportEvaluationResult.model_json_schema()

    def build_prompt(self, dialogue: str) -> str:
        return f"""
        You are an expert customer support quality analyst.
        Analyze the following dialogue between a Customer and a Support Agent and provide a structured assessment in JSON format.
        
        DIALOGUE:
        {dialogue}
        
        Your task is to evaluate the dialogue based on these strict rules:
        1. intent - MUST be one of: payment_troubles, technical_errors, account_access, tariff_questions, refund, other.
        2. satisfaction - MUST be one of: satisfied, neutral, unsatisfied. 
           CRITICAL: Some customers might display "hidden dissatisfaction". They may formally say "thank you" or "okay", but if their problem was NOT actually resolved or the agent provided useless info, mark it as 'unsatisfied' or 'neutral'.
        3. quality_score - rate on scale 1-5. 5 is only for perfect resolution and polite tone.
        4. agent_mistakes - be very strict:
           - "ignored_question": if the customer asked for multiple things and the agent missed even one.
           - "no_resolution": if the chat ended without a clear solution or next steps.
           - "incorrect_info": if the agent provided factually wrong data.
           - "rude_tone": if the agent was dismissive, impatient, or unprofessional.
           - "unnecessary_escalation": if the agent shifted the problem to another department when they could have solved it.
           If there are no mistakes, return ["none"].
        5. rationale - provide a brief (1-2 sentences) explanation.

        Return a VALID JSON object with these EXACT keys: "intent", "satisfaction", "quality_score", "agent_mistakes", "rationale".
        """

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