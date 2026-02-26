import os
from groq import Groq
from typing import Optional, Any
from providers.base import LLMProvider
from dotenv import load_dotenv

load_dotenv()

class GroqProvider(LLMProvider):
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None, response_schema: Optional[Any] = None) -> str:
        # Groq doesn't support schema directly in the same way, but supports JSON mode
        extra_args = {}
        if response_schema:
             extra_args["response_format"] = {"type": "json_object"}
             if "json" not in prompt.lower() and (not system_prompt or "json" not in system_prompt.lower()):
                 prompt += "\n\nReturn the result in JSON format."

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
            **extra_args
        )
        return completion.choices[0].message.content

    def name(self) -> str:
        return "groq"
