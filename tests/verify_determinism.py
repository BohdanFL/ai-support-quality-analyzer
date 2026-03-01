import os
from providers.ollama import OllamaProvider
from providers.gemini import GeminiProvider
from providers.groq import GroqProvider

def verify_provider(provider, name):
    print(f"\nVerifying {name}...")
    prompt = "Tell me a very short 1-sentence joke about a cat."
    
    outputs = []
    for i in range(10):
        try:
            output = provider.generate(prompt)
            outputs.append(output)
            print(f"Run {i+1}: {output}")
        except Exception as e:
            print(f"Run {i+1} failed: {e}")
            return

    if all(o == outputs[0] for o in outputs):
        print(f"SUCCESS: {name} is deterministic.")
    else:
        print(f"FAILURE: {name} is NOT deterministic.")

if __name__ == "__main__":
    # Test Ollama if available
    try:
        # ollama = OllamaProvider()
        verify_provider(ollama, "Ollama")
    except Exception as e:
        print(f"Ollama skip: {e}")

    # Test Gemini if API key set
    if os.getenv("GEMINI_API_KEY"):
        try:
            gemini = GeminiProvider()
            verify_provider(gemini, "Gemini")
        except Exception as e:
            print(f"Gemini skip: {e}")
    else:
        print("Gemini skip: No API key")

    # Test Groq if API key set
    if os.getenv("GROQ_API_KEY"):
        try:
            # groq = GroqProvider()
            verify_provider(groq, "Groq")
        except Exception as e:
            print(f"Groq skip: {e}")
    else:
        print("Groq skip: No API key")
