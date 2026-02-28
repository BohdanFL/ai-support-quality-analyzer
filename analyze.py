from llm_factory import get_llm_provider

import argparse
import json
import os
from typing import Dict

from judge_agent.evaluation_agent import LLMJudge

def analyze_chat(judge: LLMJudge, chat_data: Dict) -> Dict:
    # Convert chat messages to a readable string for the judge
    messages_str = ""
    for msg in chat_data.get("messages", []):
        role = "Customer" if msg["role"] == "user" else "Agent"
        messages_str += f"{role}: {msg['content']}\n"
    
    # The judge evaluates the dialogue using the registered metrics
    results = judge.evaluate_dialogue(messages_str)
    
    # Since we only use one metric for now, we return its result
    # We can also return the whole Dict[metric_name, result] if needed
    return results.get("support_quality_analysis", results)

def main():
    parser = argparse.ArgumentParser(description="Analyze support chat dataset")
    parser.add_argument("--provider", type=str, default="gemini", help="LLM provider (gemini, groq, ollama)")
    parser.add_argument("--model", type=str, help="Specific model name to use")
    parser.add_argument("--input", type=str, default="generated_chats.json", help="Input JSON file")
    parser.add_argument("--output", type=str, default="analysis_results.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    provider = get_llm_provider(args.provider, model_name=args.model)
    
    # Initialize the Judge with metrics
    judge = LLMJudge(provider=provider)
    
    results = []
    
    print(f"Analyzing {len(dataset)} chats using {args.provider}...")
    
    for i, chat in enumerate(dataset):
        if not chat or "error" in chat:
            print(f"[{i+1}/{len(dataset)}] Skipping invalid chat.")
            continue
            
        print(f"[{i+1}/{len(dataset)}] Analyzing chat...")
        analysis = analyze_chat(judge, chat)
        
        # Combine original chat with its analysis for the final report
        results.append({
            "chat_id": i + 1,
            "original_chat": chat,
            "analysis": analysis
        })
        
    with open("data/" + args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved analysis results to {args.output}")

if __name__ == "__main__":
    main()
