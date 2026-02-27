# AI Support Chat Generator & Analyst

This project implements a synthetic data generation and analysis pipeline for customer support chats, as part of the AI Test Task.

## Features
- **Multi-Model Support**: Integrated with Gemini, Groq, and local Ollama.
- **Synthetic Data Generation**: Generates varied support scenarios (payment, technical, account, etc.) with different case types (successful, conflict, agent mistakes).
- **Automated Analysis**: Evaluates chats for intent, customer satisfaction, quality score, and agent mistakes.
- **Hidden Dissatisfaction Detection**: Specific focus on identifying cases where a customer is formally polite but the issue remains unresolved.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   *Required keys*: `GEMINI_API_KEY`, `GROQ_API_KEY`.
   *For Ollama*: Ensure Ollama is running locally (`http://localhost:11434`).

## Usage

### 1. Generate Dataset
Run `generate.py` to create a synthetic chat dataset.
```bash
python generate.py --provider gemini --count 10 --output chats.json
```

Arguments:
- `--provider`: `gemini`, `groq`, or `ollama`.
- `--count`: Number of chats to generate.
- `--output`: Filepath to save the results.

### 2. Analyze Dataset
Run `analyze.py` to evaluate the generated chats.
```bash
python analyze.py --provider gemini --input chats.json --output results.json
```
Arguments:
- `--provider`: LLM used for analysis.
- `--input`: Path to the generated dataset.
- `--output`: Filepath for the analysis results.

## Project Structure
- `providers/`: LLM adapter implementations.
- `llm_factory.py`: Factory for switching providers.
- `generate.py`: Main script for data generation.
- `analyze.py`: Main script for data analysis.
