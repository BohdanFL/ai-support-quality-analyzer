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
   *Required:* `GEMINI_API_KEY`, `GROQ_API_KEY`.

## Quick Start (Local)

If you have your API keys in `.env`, you can run the entire pipeline with default arguments:

1. **Generate**: `python generate.py` (Creates `data/generated_chats.json`)
2. **Analyze**: `python analyze.py` (Creates `data/analysis_results.json`)
3. **Aggregate**: `python analytics/data_aggregator.py` (Creates `analytics/support_analytics.csv`)
4. **Dashboard**: `streamlit run analytics/streamlit_dashboard_app.py`

---

## Detailed Usage

### 1. Generate Dataset

Run `generate.py` to create a synthetic chat dataset.

```bash
# Using defaults (Gemini, 5 chats, output to data/generated_chats.json)
python generate.py

# Custom run
python generate.py --provider groq --count 10 --output data/chats.json
```

**Arguments:**
- `--provider`: `gemini` (default), `groq`, or `ollama`.
- `--model`: (Optional) Specific model ID (e.g., `gemini-2.5-flash-lite`, `llama-3.3-70b-versatile`).
- `--count`: Number of chats to generate (default: 5).
- `--output`: Filepath to save the results (default: `data/generated_chats.json`).
- `--matrix`: (Flag) Generate a full matrix of all intent/case-type combinations defined in `config.py`.

### 2. Analyze Dataset

Run `analyze.py` to evaluate the generated chats.

```bash
# Using defaults (Gemini, input from data/generated_chats.json)
python analyze.py

# Custom run
python analyze.py --provider groq --input data/chats.json --output data/results.json
```

**Arguments:**
- `--provider`: LLM provider for analysis (default: `gemini`).
- `--model`: (Optional) Specific model ID.
- `--input`: Path to the generated dataset (default: `data/generated_chats.json`).
- `--output`: Filepath for the analysis results (default: `data/analysis_results.json`).

### 3. Business Intelligence & Analytics

Aggregate the JSON results into a CSV for the dashboard:

```bash
# Using defaults
python analytics/data_aggregator.py
```

**Arguments:**
- `--chats`: (Default: `data/generated_chats.json`)
- `--results`: (Default: `data/analysis_results.json`)
- `--output`: (Default: `analytics/support_analytics.csv`)

### 4. Interactive Dashboard

Review the results visually:

```bash
streamlit run analytics/streamlit_dashboard_app.py
```

---

## Docker Support

If you prefer using Docker (especially for local Ollama models):

1. **Start Containers**:
   ```bash
   docker-compose up -d --build
   ```

2. **Run Pipeline inside Container**:
   ```bash
   docker exec -it llm_analytics python3 generate.py --provider ollama
   docker exec -it llm_analytics python3 analyze.py --provider ollama
   docker exec -it llm_analytics python3 analytics/data_aggregator.py
   ```

## Project Structure

- `providers/`: LLM adapter implementations (Gemini, Groq, Ollama).
- `judge_agent/`: Core analysis logic.
  - `config.py`: Central configuration for personas, intents, and behavior types.
  - `evaluation_agent.py`: Implementation of the AI evaluation logic.
  - `models.py`: Pydantic data models for structured LLM input/output.
- `prompts/`: Template library for system prompts and evaluation metrics.
- `analytics/`: Business intelligence tools.
  - `data_aggregator.py`: Script to merge chats and analysis into a CSV.
  - `streamlit_dashboard_app.py`: Interactive dashboard for visualizing results.
- `data/`: Storage for generated datasets and analysis results.
- `llm_factory.py`: Central factory to switch between LLM providers.
- `generate.py`: Entry point for synthetic chat generation.
- `analyze.py`: Entry point for automated quality analysis.
