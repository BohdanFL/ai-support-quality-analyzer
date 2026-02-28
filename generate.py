import argparse
import json
import os
from typing import List, Dict, Any
from llm_factory import get_llm_provider
from judge_agent.models import SupportChat
from judge_agent.config import (
    INTENTS, CASE_TYPES, AGENT_PERSONAS, 
    CUSTOMER_PERSONAS, MISTAKE_TYPES
)
from pathlib import Path
import random
import logging

# Configure logging to show retry attempts from tenacity
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants
DEFAULT_OUTPUT_PATH = "data/generated_chats.json"
SYSTEM_PROMPT_PATH = "prompts/generation_system.md"

def generate_chat(provider, scenario: str, case_type: str, system_prompt: str) -> Dict[str, Any]:
    agent_p = random.choice(AGENT_PERSONAS)
    customer_p = random.choice(CUSTOMER_PERSONAS)
    
    is_hidden_dissatisfaction = False
    if case_type == "problematic":
        # 70% chance to be hidden dissatisfaction in problematic cases
        is_hidden_dissatisfaction = random.random() < 0.7

    chosen_mistakes = []
    mistake_description = ""
    if case_type == "agent_mistake":
        # Pick 1-2 random mistakes
        mistakes_objs = random.sample(MISTAKE_TYPES, k=random.randint(1, 2))
        chosen_mistakes = [m["name"] for m in mistakes_objs]
        mistake_description = "The agent MUST make these specific mistakes:\n" + \
                             "\n".join([f"- {m['name']}: {m['description']}" for m in mistakes_objs])

    hidden_diss_instruction = ""
    if is_hidden_dissatisfaction:
        hidden_diss_instruction = (
            "IMPORTANT: This is a 'Hidden Dissatisfaction' case. "
            "The customer MUST end the chat saying 'thank you' or 'okay', "
            "but it should be clear from the context that their problem was NOT actually solved "
            "or the solution was extremely frustrating."
        )

    prompt = (
        f"Generate a realistic customer support chat about '{scenario}'.\n"
        f"Primary Case Type: '{case_type}'.\n\n"
        f"AGENT PERSONA: {agent_p['name']}\nDetails: {agent_p['description']}\n\n"
        f"CUSTOMER PERSONA: {customer_p['name']}\nDetails: {customer_p['description']}\n\n"
        f"{mistake_description}\n\n"
        f"{hidden_diss_instruction}\n\n"
        "Ensure the dialogue reflects these identities and behavioral constraints naturally."
    )
    
    metadata = {
        "agent_persona": agent_p["name"],
        "customer_persona": customer_p["name"],
        "is_hidden_dissatisfaction": is_hidden_dissatisfaction,
        "intended_mistakes": chosen_mistakes if case_type == "agent_mistake" else []
    }

    validated_chat = provider.generate(
        prompt, 
        system_prompt=system_prompt,
        response_model=SupportChat
    )
    
    if not validated_chat:
        return {"error": "Failed to parse/validate"}
    
    chat_dict = validated_chat.model_dump()
    chat_dict["metadata"] = metadata
    return chat_dict

def main():
    logging.warning("Logging system active. If you see retries, they will appear below.")
    parser = argparse.ArgumentParser(description="Generate support chat dataset")
    parser.add_argument("--provider", type=str, default="gemini", help="LLM provider (gemini, groq, ollama)")
    parser.add_argument("--model", type=str, help="Specific model name to use")
    parser.add_argument("--count", type=int, default=5, help="Number of chats to generate")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_PATH, help="Output file")
    parser.add_argument("--matrix", action="store_true", help="Generate matrix (one for each intent/case_type combination)")
    
    args = parser.parse_args()
    
    provider = get_llm_provider(args.provider, model_name=args.model)

    # Load generation system prompt
    try:
        system_prompt = Path(SYSTEM_PROMPT_PATH).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: System prompt file {SYSTEM_PROMPT_PATH} not found.")
        return
    
    dataset = []
    if os.path.exists(args.output):
        try:
            with open(args.output, "r", encoding="utf-8") as f:
                dataset = json.load(f)
        except:
            dataset = []

    # Checkpointing: count existing (intent, case_type) pairs
    existing_counts = {}
    for entry in dataset:
        key = (entry.get("intent"), entry.get("type"))
        existing_counts[key] = existing_counts.get(key, 0) + 1

    pairs_to_generate = []
    if args.matrix:
        # For matrix, we generate all combinations once
        for intent in INTENTS:
            for case_type in CASE_TYPES:
                pairs_to_generate.append((intent, case_type))
    else:
        # Generate exactly --count samples
        for i in range(args.count):
            intent = INTENTS[i % len(INTENTS)]
            case_type = CASE_TYPES[i % len(CASE_TYPES)]
            pairs_to_generate.append((intent, case_type))

    # Filter out already generated pairs
    final_pairs = []
    for intent, case_type in pairs_to_generate:
        key = (intent, case_type)
        if existing_counts.get(key, 0) > 0:
            existing_counts[key] -= 1
            continue
        final_pairs.append((intent, case_type))

    if not final_pairs:
        print("All requested chats already exist in the output file. Nothing to generate.")
        return

    print(f"Plan to generate {len(final_pairs)} NEW chats using {args.provider} (Skipped {len(pairs_to_generate) - len(final_pairs)} existing matches)...")

    output_dir = os.path.dirname("data/" + args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    for i, (intent, case_type) in enumerate(final_pairs):
        print(f"[{i+1}/{len(pairs_to_generate)}] Generating {case_type} for {intent}...")
        chat = generate_chat(provider, intent, case_type, system_prompt)
        
        if "error" not in chat:
            dataset.append(chat)
            # Intermediate save
            with open("data/" + args.output, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
        else:
            print(f"Error generating chat for {intent}: {chat['error']}")
        
    print(f"Successfully finished. Dataset size: {len(dataset)} records in {args.output}")

if __name__ == "__main__":
    main()
