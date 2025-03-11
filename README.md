# AI Guardian: Prompt Injection Defense System

AI Guardian is a demonstration system that showcases prompt injection defense techniques for Large Language Models (LLMs). It provides real-time detection and sanitization of potential prompt injection attacks while allowing legitimate prompts to pass through.

## Features

- **Real-time Injection Detection**: Monitors user inputs for common prompt injection patterns
- **Pattern-based Analysis**: Uses regex patterns to identify both malicious and safe patterns
- **Input Sanitization**: Automatically redacts potentially harmful content
- **Statistics Visualization**: Tracks and displays attempt statistics in real-time
- **Open Source Model Integration**: Uses Hugging Face's transformers library with open-source models

## Technical Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly Express
- **ML Framework**: Hugging Face Transformers
- **Default Model**: distilgpt2 (configurable)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-guardian.git
cd ai-guardian
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run main.py
```

2. Access the web interface (typically http://localhost:8501)
3. Enter prompts in the text area
4. Click "Generate Response" to test the input

## Configuration

The system can be configured through environment variables:

- `MODEL_NAME`: Change the Hugging Face model (default: "distilgpt2")

Other supported models include:
- gpt2
- EleutherAI/pythia-160m
- cerebras/Cerebras-GPT-111M

## Security Features

### Injection Detection
- Pattern-based detection of common prompt injection attempts
- Safe pattern recognition to reduce false positives
- Logging of detected injection attempts

### Input Sanitization
- Automatic redaction of potentially harmful content
- Preservation of safe content
- Real-time feedback on detected threats

## Statistics

The system maintains two key metrics:
- **Total Attempts**: All prompt submissions
- **Blocked Attempts**: Successfully detected injection attempts

## Project Structure

```
ai-guardian/
├── main.py               # Main Streamlit application
├── config.py            # Model configuration settings
├── requirements.txt     # Project dependencies
├── core/
│   ├── __init__.py     # Core package initialization
│   ├── interfaces.py   # Abstract base classes
│   └── model_handler.py # Model loading and inference
├── components/
│   ├── __init__.py     # Components package initialization
│   ├── input.py        # User input handling
│   ├── metrics.py      # Analytics dashboard
│   └── visualizations.py # Security visualizations
├── utils/
│   ├── __init__.py     # Utils package initialization
│   └── utils.py        # Security utility functions
└── tests/
    ├── __init__.py     # Tests package initialization
    └── test_security.py # Security features testing
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Hugging Face for providing access to their LLMs.
- Streamlit for the interactive web interface.
- Plotly for the visualization tools.
- The AI safety and security community for their research and insights.

## ⚠️ Disclaimer

This tool is intended for educational and defensive purposes only. Users are responsible for complying with the terms of service and ethical guidelines of all LLM providers.