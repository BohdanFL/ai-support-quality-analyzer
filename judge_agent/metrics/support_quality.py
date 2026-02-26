import json
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator
from judge_agent.metrics.metrics_base import Metric

class SupportEvaluationResult(BaseModel):
    intent: Literal[
        "payment_troubles", 
        "technical_errors", 
        "account_access", 
        "tariff_questions", 
        "refund", 
        "other"
    ] = Field(
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
        description="List of support's mistakes. If there are none, return ['none']."
    )
    rationale: str = Field(
        description="Brief (1-2 sentences) explanation on why such rate was given."
    )

    @field_validator("intent", "satisfaction", mode="before")
    @classmethod
    def normalize_fields(cls, v: str) -> str:
        if not isinstance(v, str):
            return v
        v = v.lower().replace(" ", "_")
        if "tender" in v: return "tariff_questions" # heuristic
        if "payment" in v: return "payment_troubles"
        if "technical" in v: return "technical_errors"
        if "account" in v: return "account_access"
        if "price" in v: return "tariff_questions"
        return v

    @field_validator("agent_mistakes", mode="before")
    @classmethod
    def normalize_mistakes(cls, v: Any) -> List[str]:
        if isinstance(v, str): v = [v]
        if not isinstance(v, list): return v
        return [i.lower() for i in v if isinstance(i, str)]

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