# Swagger AI Agent

An intelligent agent that helps users interact with APIs using natural language by parsing Swagger/OpenAPI specifications.

## Features

- Parse and validate Swagger/OpenAPI specifications
- Natural language understanding of API endpoints using local LLM (Ollama)
- Intelligent parameter collection and validation
- Automatic API request execution
- User-friendly Streamlit interface

## Prerequisites

- Python 3.8+
- Ollama installed with llama2 model
- Virtual environment (recommended)

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run src/main.py
```

2. The web interface will automatically open in your default browser

## How to Use

1. Upload your Swagger/OpenAPI specification file (JSON format)
2. Enter the base URL of your API
3. Type your intent in natural language (e.g., "I want to create a new user")
4. Click "Process Request"

The agent will:
1. Parse and validate the Swagger specification
2. Use the local LLM to understand your intent
3. Match your intent with available API endpoints
4. Guide you through parameter collection
5. Execute the API request and show the response

## How it Works

1. The agent first parses and validates the provided Swagger/OpenAPI specification
2. When you enter your intent, the agent:
   - Uses the local LLM to understand the intent
   - Matches the intent with available API endpoints
   - Guides you through parameter collection
   - Executes the API request with the collected parameters
3. The agent displays the API response along with details about the chosen endpoint and parameters

## Error Handling

- Invalid Swagger specifications will be rejected
- Missing required parameters will be reported
- API execution errors will be properly handled and reported

## Security Considerations

- The agent runs locally and uses Ollama for LLM functionality
- No data is sent to external services
- API keys and sensitive data should be handled securely
