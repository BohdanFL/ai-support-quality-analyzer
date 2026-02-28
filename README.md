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

    _Required keys_: `GEMINI_API_KEY`, `GROQ_API_KEY`.
    _For Ollama_: Ensure Ollama is running locally (`http://localhost:11434`).

3. **Run the script**:

    ### Build the Build and Start Containers:

    # Start with Ollama (local models)

    ```bash
    docker-compose up -d --build
    ```

    # Start without Ollama (with API keys)

    ```bash
    docker-compose --profile without-ollama up -d --build
    ```

    ### Verify Containers are Running

    ```bash
    docker-compose ps -a
    ```

    ### Download Required AI Model

    ```bash
    docker exec ollama-server ollama pull llama2
    ```

    ### You can also pull other models:

    ```bash
    docker exec ollama-server ollama pull phi3:mini
    docker exec ollama-server ollama pull mistral
    docker exec ollama-server ollama pull llama3:8b-instruct-q4_K_M
    ```

    ### Access Your Application Container

    ```baSH
    docker exec -it llm_analytics /bin/bash
    ```

    ### Generate Dataset Inside Container

    ```bash
    python3 generate.py --provider ollama --count 10 --output /app/output/chats.json
    ```

    ### Analyze Dataset

    ```bash
    python analyze.py --provider ollama --input /app/output/chats.json --output /app/output/results.json
    ```

    ### View Generated Results

    ```bash
    ls -la output/
    cat output/chats.json
    ```

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

### 3. Business Intelligence & Analytics

Run the aggregator with default file names **(Works in container)**:

```bash
python data_aggregator.py
```

This expects:

- generated_chats.json - Your chat dataset
- analysis_results.json - Your analysis results

Script creates support\*analytics.csv that will be used in streamlit_dashboard_app.py for visualizing and exploring support chat analytics in Streamlit Dashboard **(Doesn't work in container)**.

```bash
streamlit run streamlit_dashboard_app.py
```

This will:

- Start a local web server
- Automatically open your browser to `http://localhost:8501`
- Load and display the analytics data
  Access the Dashboard

If the browser doesn't open automatically, navigate to:

- Local URL: `http://localhost:8501`
- Network URL: `http://192.168.1.xxx:8501` (for other devices on your network)

## Project Structure

- `providers/`: LLM adapter implementations.
- `llm_factory.py`: Factory for switching providers.
- `generate.py`: Main script for data generation.
- `analyze.py`: Main script for data analysis.
