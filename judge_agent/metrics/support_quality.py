import json
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field, ValidationError
from judge_agent.metrics.metrics_base import Metric

class SupportEvaluationResult(BaseModel):
    intent: List[Literal[
        "payment_troubles", 
        "technical_errors", 
        "account_access", 
        "refund", 
        "other"
    ]] = Field(
        description="Client's request category. If none fits return 'other'."
    )
    satisfaction: Literal["satisfied", "neutral", "unsatisfied"] = Field(
        description="Level of satisfaction of the client at the end of the communication."
    )
    quality_score: int = Field(
        ge=1, le=5, 
        description="Support's quality rate on the scale from 1 to 5 where 1 is terrible response and 5 is perfect response."
    )
    agent_mistakes: List[Literal[
        "ignored_question", 
        "incorrect_info", 
        "rude_tone", 
        "no_resolution", 
        "unnecessary_escalation",
        "none"
    ]] = Field(
        description="List of support's mistakes. If there are none, return 'none'."
    )
    rationale: str = Field(
        description="Brief (1-2 sentences) explanation on why such rate was given."
    )

class SupportQualityMetric(Metric):
    @property
    def name(self) -> str:
        return "support_quality_analysis"
    
    @property
    def response_schema(self) -> Optional[Dict[str, Any]]:
        # Повертаємо Pydantic схему окремим словником
        return SupportEvaluationResult.model_json_schema()

    def build_prompt(self, dialogue: str) -> str:
        
        return f"""
        You are an experienced QA Manager.
        Analyze the following dialogue between a Customer and a Support Agent.
        
        DIALOGUE:
        {dialogue}
        
        Your task is to evaluate the dialogue
        Important rules:
        1. satisfaction - evaluate by the tone of the customer in their latest messages.
        2. agent_mistakes - be strict. If the customer asked for two things and the agent answered one -> "ignored_question".
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