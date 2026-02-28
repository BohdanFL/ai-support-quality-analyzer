from pydantic import BaseModel, Field, field_validator, computed_field
from typing import List, Literal, Any

request_intent = Literal[
    "payment_troubles",
    "technical_errors",
    "account_access",
    "tariff_questions",
    "refund",
    "other"
]

# --- Base Models ---

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# --- Generation Models ---

class SupportChat(BaseModel):
    scenario: request_intent
    type: str = Field(description="The behavior case type (e.g., successful, hidden dissatisfaction)")
    messages: List[Message]

# --- Analysis Models ---

class SupportEvaluationResult(BaseModel):
    # It is mandatory for thought process to be the first thing LLM does before moving on to
    # the next components of answer
    thought_process: str = Field(
        description=(
            "Think step-by-step. First, analyze the client's initial request. "
            "Second, evaluate how the agent handled it. "
            "Third, identify any specific mistakes the agent made. "
            "Finally, conclude what the quality score should be."
        )
    )
    intent: request_intent = Field(
        description="Client's request category. If none fits return 'other'."
    )
    satisfaction: Literal["satisfied", "neutral", "unsatisfied"] = Field(
        description="Level of satisfaction of the client at the end of the communication. Unsatisfied client demonstrates ungratefulness and anger."
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
    is_problem_solved: bool = Field(
        description="Define if problem requested in intent was solved by the end of the chat."
    )

    @computed_field
    def hidden_unsatisfaction(self) -> bool:
        return not self.is_problem_solved and self.satisfaction != "unsatisfied"