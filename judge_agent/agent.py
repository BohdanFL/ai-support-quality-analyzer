from providers.ollama import OllamaProvider

provider = OllamaProvider("llama3.1:8b")

response = provider.generate("Привітики")

print(response)