from llm_factory import get_llm_provider
from judge_agent.models import SupportChat
import argparse
import json
from typing import Dict

# Scenarios as defined in the task
SCENARIOS = [
    "payment issues",
    "technical errors",
    "account access",
    "tariff_questions",
    "refund requests"
]

# Types of cases needed
CASE_TYPES = [
    "successful case",
    "problematic case",
    "conflict case",
    "agent mistake (ignored question)",
    "agent mistake (incorrect info)",
    "agent mistake (rude tone)",
    "hidden dissatisfaction (client formally thanks but problem unresolved)"
]

GENERATION_SYSTEM_PROMPT = """
You are a synthetic data generator for customer support chats. 
Your goal is to generate realistic dialogues between a Customer and a Support Agent.

Each dialogue should be a JSON object with:
- "scenario": The topic of the chat.
- "type": The specific behavior case (e.g., successful, conflict, agent mistake).
- "messages": An array of objects with "role" (user or assistant) and "content".

Make the dialogues feel natural, not overly robotic. Support agents should try to be helpful but can make mistakes if specified by the type.
"""

def generate_chat(provider, scenario: str, case_type: str) -> Dict:
    prompt = f"Generate a realistic customer support chat about '{scenario}'. The case type is: '{case_type}'."
    
    # Instructor returns a parsed Pydantic model
    validated_chat = provider.generate(
        prompt, 
        system_prompt=GENERATION_SYSTEM_PROMPT,
        response_model=SupportChat
    )
    
    if not validated_chat:
        return {"error": "Failed to parse/validate"}
    
    return validated_chat.model_dump()

def main():
    parser = argparse.ArgumentParser(description="Generate support chat dataset")
    parser.add_argument("--provider", type=str, default="gemini", help="LLM provider (gemini, groq, ollama)")
    parser.add_argument("--count", type=int, default=5, help="Number of chats to generate")
    parser.add_argument("--output", type=str, default="generated_chats.json", help="Output file")
    
    args = parser.parse_args()
    
    provider = get_llm_provider(args.provider)
    dataset = []
    
    print(f"Generating {args.count} chats using {args.provider}...")

    for i in range(args.count):
        scenario = SCENARIOS[i % len(SCENARIOS)]
        case_type = CASE_TYPES[i % len(CASE_TYPES)]
        print(f"[{i+1}/{args.count}] Generating {case_type} for {scenario}...")
        chat = generate_chat(provider, scenario, case_type)
        dataset.append(chat)
        
    with open("data/" + args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated dataset to {args.output}")

if __name__ == "__main__":
    main()
