import os
import google.generativeai as genai
from typing import Optional
from providers.base import LLMProvider
from dotenv import load_dotenv

load_dotenv()

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self._model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if system_prompt:
            # Gemini 1.5 supports system_instruction
            model = genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
        else:
            response = self.model.generate_content(prompt)
        
        return response.text

    def name(self) -> str:
        return "gemini"
