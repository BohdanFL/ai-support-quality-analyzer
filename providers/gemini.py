import os
from google import genai
import instructor
from providers.base import LLMProvider
from dotenv import load_dotenv

load_dotenv()

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemma-3-27b-it"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.model_name = model_name
        self.client = instructor.from_genai(
            genai.Client(api_key=api_key),
            mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS,
        )

    def _get_generation_kwargs(self) -> dict:
        return {
            "model": self.model_name,
            "config": {"temperature": 0}
        }

    def name(self) -> str:
        return "gemini"

