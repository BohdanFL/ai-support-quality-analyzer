from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional

# --- Generation Models ---

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class SupportChat(BaseModel):
    scenario: Literal[
        "payment issues",
        "technical errors",
        "account access",
        "pricing questions",
        "refund requests"
    ]
    type: str = Field(description="The behavior case type (e.g., successful, hidden dissatisfaction)")
    messages: List[Message]

    @field_validator("scenario", mode="before")
    @classmethod
    def normalize_scenario(cls, v: str) -> str:
        return v.lower() if isinstance(v, str) else v

# --- Analysis Models ---

class AnalysisResult(BaseModel):
    intent: Literal[
        "payment issues",
        "technical errors",
        "account access",
        "pricing questions",
        "refund requests",
        "other"
    ]
    satisfaction: Literal["satisfied", "neutral", "unsatisfied"]
    quality_score: int = Field(ge=1, le=5)
    agent_mistakes: List[Literal[
        "ignored_question",
        "incorrect_info",
        "rude_tone",
        "no_resolution",
        "unnecessary_escalation"
    ]]

    @field_validator("intent", "satisfaction", mode="before")
    @classmethod
    def normalize_fields(cls, v: str) -> str:
        return v.lower() if isinstance(v, str) else v

    @field_validator("agent_mistakes", mode="before")
    @classmethod
    def normalize_list(cls, v: List[str]) -> List[str]:
        if isinstance(v, list):
            return [i.lower() for i in v if isinstance(i, str)]
        return v
