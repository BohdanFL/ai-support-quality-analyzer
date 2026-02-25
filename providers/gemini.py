import os
from google import genai
from typing import Optional, Any
from providers.base import LLMProvider
from dotenv import load_dotenv

load_dotenv()

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_schema: Optional[Any] = None) -> str:
        config = {}
        if system_prompt:
            config['system_instruction'] = system_prompt
        
        if response_schema:
            config['response_mime_type'] = 'application/json'
            config['response_schema'] = response_schema
            
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            # Fallback for models that might not support system_instruction via the config
            if "Developer instruction is not enabled" in str(e) and system_prompt:
                # Combine system prompt with user prompt as a fallback
                combined_prompt = f"System Instruction: {system_prompt}\n\nUser: {prompt}"
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=combined_prompt
                )
                return response.text
            raise e

    def name(self) -> str:
        return "gemini"
