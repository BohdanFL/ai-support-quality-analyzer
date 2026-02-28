import argparse
import json
import os
from typing import List, Dict, Any
from llm_factory import get_llm_provider
from judge_agent.models import SupportChat
import random

# Constants
DEFAULT_OUTPUT_PATH = "data/generated_chats.json"

INTENTS = [
    "payment_troubles",
    "technical_errors",
    "account_access",
    "tariff_questions",
    "refund"
]

CASE_TYPES = [
    "successful",
    "problematic",
    "conflict",
    "agent_mistake"
]

AGENT_PERSONAS = [
    {
        "name": "Experienced Professional",
        "description": "Calm, efficient, follows protocol accurately, empathetic but maintains professional boundaries."
    },
    {
        "name": "Impatient Trainee",
        "description": "Fast but slightly sloppy, relies heavily on canned responses, gets visibly annoyed with long customer explanations."
    },
    {
        "name": "Overly Polite Senior",
        "description": "Uses extremely formal and flowery language, apologizes excessively for every minor inconvenience, very thorough but perhaps too slow."
    },
    {
        "name": "Strictly-by-the-Book Agent",
        "description": "Cold, literal, lacks empathy, refuses to deviate from scripts even when they don't apply well to the situation."
    }
]

CUSTOMER_PERSONAS = [
    {
        "name": "Tech-savvy Millennial",
        "description": "Impatient with basic troubleshooting steps, wants direct and technical answers, uses modern slang and concise sentences."
    },
    {
        "name": "Elderly Person",
        "description": "Confused by technical terminology, needs slow and step-by-step explanations, very polite and appreciative of patience."
    },
    {
        "name": "Busy Entrepreneur",
        "description": "Multitasking and distracted, sends short and urgent messages, gets frustrated by any delays or repeat questions."
    },
    {
        "name": "Angry Student",
        "description": "Feels entitled and treated unfairly, aggressive and demanding, uses exclamation marks and caps for emphasis."
    },
    {
        "name": "Polite but Persistent Customer",
        "description": "Extremely detail-oriented, won't end the chat until every single sub-question is answered, very observant of agent's tone."
    }
]

MISTAKE_TYPES = [
    {
        "name": "ignored_question",
        "description": "The agent completely ignores one or more specific questions or concerns raised by the customer."
    },
    {
        "name": "incorrect_info",
        "description": "The agent provides factually wrong information about the product, technical steps, or company policy."
    },
    {
        "name": "rude_tone",
        "description": "The agent's tone is dismissive, passive-aggressive, or overtly rude to the customer."
    },
    {
        "name": "no_resolution",
        "description": "The agent ends the interaction without actually solving the customer's primary problem despite saying they are finished."
    },
    {
        "name": "unnecessary_escalation",
        "description": "The agent transfers the customer to another department for a basic issue they should have been able to handle themselves."
    }
]

GENERATION_SYSTEM_PROMPT = """
You are a synthetic data generator for customer support chats. 
Your goal is to generate realistic dialogues between a Customer and a Support Agent.

Each dialogue should be a JSON object with:
- "scenario": The topic of the chat.
- "type": The specific behavior case (successful, problematic, conflict, or agent_mistake).
- "metadata": Detailed information about the personalities and intended behaviors.
- "messages": An array of objects with "role" (user or assistant) and "content".

Make the dialogues feel natural. Support agents should try to be helpful but can make mistakes if specified.
"""

def generate_chat(provider, scenario: str, case_type: str) -> Dict[str, Any]:
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
        system_prompt=GENERATION_SYSTEM_PROMPT,
        response_model=SupportChat
    )
    
    if not validated_chat:
        return {"error": "Failed to parse/validate"}
    
    chat_dict = validated_chat.model_dump()
    chat_dict["metadata"] = metadata
    return chat_dict

def main():
    parser = argparse.ArgumentParser(description="Generate support chat dataset")
    parser.add_argument("--provider", type=str, default="gemini", help="LLM provider (gemini, groq, ollama)")
    parser.add_argument("--count", type=int, default=5, help="Number of chats to generate")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_PATH, help="Output file")
    parser.add_argument("--matrix", action="store_true", help="Generate matrix (one for each intent/case_type combination)")
    
    args = parser.parse_args()
    
    provider = get_llm_provider(args.provider)
    
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
        chat = generate_chat(provider, intent, case_type)
        
        if "error" not in chat:
            dataset.append(chat)
            # Intermediate save
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
        else:
            print(f"Error generating chat for {intent}: {chat['error']}")
        
    print(f"Successfully finished. Dataset size: {len(dataset)} records in {args.output}")

if __name__ == "__main__":
    main()
