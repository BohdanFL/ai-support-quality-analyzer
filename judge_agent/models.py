from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional, Any

# --- Base Models ---

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# --- Generation Models ---

class SupportChat(BaseModel):
    scenario: Literal[
        "payment_troubles",
        "technical_errors",
        "account_access",
        "tariff_questions",
        "refund",
        "other"
    ]
    type: str = Field(description="The behavior case type (e.g., successful, hidden dissatisfaction)")
    messages: List[Message]

# --- Analysis Models ---

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
