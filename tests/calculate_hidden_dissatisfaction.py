import json
import os

def analyze_hidden_dissatisfaction(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_chats = len(data)
    actual_hidden_dissatisfaction = 0
    analyzed_hidden_dissatisfaction = 0
    matches = 0
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0

    for entry in data:
        # Actual value from metadata
        reality = entry.get('original_chat', {}).get('metadata', {}).get('is_hidden_dissatisfaction', False)
        # Analyzed value from LLM
        analysis = entry.get('analysis', {}).get('result', {}).get('hidden_unsatisfaction', False)

        if reality:
            actual_hidden_dissatisfaction += 1
        if analysis:
            analyzed_hidden_dissatisfaction += 1

        if reality == analysis:
            matches += 1
            if reality:
                true_positives += 1
            else:
                true_negatives += 1
        else:
            if analysis:
                false_positives += 1
            else:
                false_negatives += 1

    match_percentage = (matches / total_chats) * 100 if total_chats > 0 else 0
    
    # Specific accuracy for positive cases (recall/precision related)
    # How many of the ACTUAL hidden dissatisfactions were caught?
    catch_rate = (true_positives / actual_hidden_dissatisfaction) * 100 if actual_hidden_dissatisfaction > 0 else 0

    print("--- Hidden Dissatisfaction Analysis ---")
    print(f"Total Chats processed: {total_chats}")
    print(f"Actual Hidden Dissatisfaction (Truth): {actual_hidden_dissatisfaction}")
    print(f"Analyzed Hidden Dissatisfaction (LLM): {analyzed_hidden_dissatisfaction}")
    print("-" * 40)
    print(f"Overall Match (Accuracy): {matches} / {total_chats} ({match_percentage:.2f}%)")
    print(f"Catch Rate (Recall): {true_positives} / {actual_hidden_dissatisfaction} ({catch_rate:.2f}%)")
    print("-" * 40)
    print(f"True Positives:  {true_positives}")
    print(f"True Negatives:  {true_negatives}")
    print(f"False Positives: {false_positives}")
    print(f"False Negatives: {false_negatives}")

if __name__ == "__main__":
    file_path = r"d:\User\Desktop\IT\projects\int20h-2026-hackaton\test-task\gemini_analysis.json"
    analyze_hidden_dissatisfaction(file_path)
