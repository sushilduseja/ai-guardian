# AI Guardian: Prompt Injection Defense System

AI Guardian is a demonstration system that showcases prompt injection defense techniques for Large Language Models (LLMs). It provides real-time detection and sanitization of potential prompt injection attacks while allowing legitimate prompts to pass through.

## Features

- **Real-time Injection Detection**: Monitors user inputs for common prompt injection patterns
- **Pattern-based Analysis**: Uses regex patterns to identify both malicious and safe patterns
- **Input Sanitization**: Automatically redacts potentially harmful content
- **Statistics Visualization**: Tracks and displays attempt statistics in real-time
- **Groq API Integration**: Uses Groq's fast inference API with current free-tier models
- **UI Enhancements**: Clear-text icon overlay in textarea, session reset button, real-time character counter

## Technical Stack

- **Frontend**: Streamlit (≥1.24.0)
- **Visualization**: Plotly Express
- **LLM API**: Groq (free-tier models)
- **Default Model**: llama-3.1-8b-instant

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sushilduseja/ai-guardian.git
cd ai-guardian
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set your Groq API key:
```bash
# Create a .env file in the project root
echo GROQ_API_KEY=<your-key> > .env
```

Get a free key at https://console.groq.com/keys

## Usage

1. Start the Streamlit application:
```bash
streamlit run main.py
```

2. Access the web interface (typically http://localhost:8501)
3. Select a model from the sidebar (optional; defaults to Llama 3.1 8B)
4. Enter prompts in the text area (click the ✕ icon to clear)
5. Click "Generate Response" to test the input
6. Use "Reset UI to initial state" button to clear metrics and start fresh

## Configuration

The system can be configured through the `.env` file:

- `GROQ_API_KEY`: Your Groq API key (required)

Model selection is available via the sidebar dropdown (Groq free-tier):

- **Llama 3.1 8B Instant** (default) — fast, current Groq text model
- **Llama 3.3 70B Versatile** — higher quality reasoning and longer context
- **Llama 4 Scout** — latest instruction-tuned general-purpose model
- **Qwen 3 32B** — multilingual, long-form generation

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
├── main.py                    # Main Streamlit application
├── src/                       # Application package
│   ├── config.py             # Groq model configuration
│   ├── state.py              # Session state management
│   ├── detection.py          # Injection detection & sanitization
│   ├── model/
│   │   ├── interfaces.py     # Abstract base classes
│   │   └── handler.py        # Groq API handler
│   └── ui/
│       ├── input.py          # User input handling
│       ├── metrics.py        # Analytics dashboard
│       ├── model_selector.py # Model selection
│       └── visualizations.py # Security visualizations
├── tests/
│   ├── test_detection.py     # Detection tests
│   ├── test_model_handler.py # Handler tests
│   └── test_state.py         # State tests
├── .env / .env.example       # Configuration
├── requirements.txt          # Dependencies
└── pyproject.toml            # Project metadata
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Groq for providing fast LLM inference API.
- Streamlit for the interactive web interface.
- Plotly for the visualization tools.
- The AI safety and security community for their research and insights.

## ⚠️ Disclaimer

This tool is intended for educational and defensive purposes only. Users are responsible for complying with the terms of service and ethical guidelines of all LLM providers.
