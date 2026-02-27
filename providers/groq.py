import os
from groq import Groq
from typing import Optional, Any, Type
from pydantic import BaseModel
import instructor
from providers.base import LLMProvider
from dotenv import load_dotenv

load_dotenv()

class GroqProvider(LLMProvider):
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = instructor.from_groq(Groq(api_key=api_key), mode=instructor.Mode.JSON)
        self.model_name = model_name

    def _get_generation_kwargs(self) -> dict:
        return {
            "model": self.model_name,
            "temperature": 0,
            "max_tokens": 2048,
            "seed": 42,
        }

    def name(self) -> str:
        return "groq"
