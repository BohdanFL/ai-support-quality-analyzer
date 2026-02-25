from llm_factory import get_llm_provider
import argparse
import json
import os
from typing import List, Dict, Optional

ANALYSIS_SYSTEM_PROMPT = """
You are an expert customer support quality analyst. 
Your task is to analyze a support dialogue and provide a structured assessment in JSON format.

Categories for 'intent':
- payment issues
- technical errors
- account access
- pricing questions
- refund requests
- other

Categories for 'satisfaction':
- satisfied
- neutral
- unsatisfied

Scale for 'quality_score': 1 to 5 (Integer)

Possible values for 'agent_mistakes' (as a list):
- ignored_question
- incorrect_info
- rude_tone
- no_resolution
- unnecessary_escalation
(Leave list empty if no mistakes were made)

CRITICAL: Some customers might display "hidden dissatisfaction". They may formally say "thank you" or "okay", but if their problem was NOT actually resolved or the agent provided useless info, mark it as 'unsatisfied' or 'neutral' and note the lack of resolution in 'agent_mistakes'.

Return ONLY a JSON object with these keys:
{
  "intent": "...",
  "satisfaction": "...",
  "quality_score": 0,
  "agent_mistakes": ["...", "..."]
}
"""

def analyze_chat(provider, chat_data: Dict) -> Dict:
    # Convert chat messages to a readable string for the LLM
    messages_str = ""
    for msg in chat_data.get("messages", []):
        role = "Customer" if msg["role"] == "user" else "Agent"
        messages_str += f"{role}: {msg['content']}\n"
    
    prompt = f"Analyze the following support chat:\n\n{messages_str}\n\nReturn the analysis as JSON."
    
    response_text = provider.generate(prompt, system_prompt=ANALYSIS_SYSTEM_PROMPT)
    
    # Cleaning
    cleaned_response = response_text.strip()
    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response.split("\n", 1)[1]
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response.rsplit("\n", 1)[0]
    cleaned_response = cleaned_response.strip()
    if cleaned_response.startswith("json"):
        cleaned_response = cleaned_response[4:].strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from analyst response: {response_text[:100]}...")
        return {"error": "Failed to parse", "raw": response_text}

def main():
    parser = argparse.ArgumentParser(description="Analyze support chat dataset")
    parser.add_argument("--provider", type=str, default="gemini", help="LLM provider (gemini, groq, ollama)")
    parser.add_argument("--input", type=str, default="generated_chats.json", help="Input JSON file")
    parser.add_argument("--output", type=str, default="analysis_results.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    provider = get_llm_provider(args.provider)
    results = []
    
    print(f"Analyzing {len(dataset)} chats using {args.provider}...")
    
    for i, chat in enumerate(dataset):
        if "error" in chat:
            print(f"[{i+1}/{len(dataset)}] Skipping chat with generation error.")
            continue
            
        print(f"[{i+1}/{len(dataset)}] Analyzing chat...")
        analysis = analyze_chat(provider, chat)
        
        # Combine original chat with its analysis for the final report
        results.append({
            "chat_id": i + 1,
            "original_chat": chat,
            "analysis": analysis
        })
        
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved analysis results to {args.output}")

if __name__ == "__main__":
    main()
