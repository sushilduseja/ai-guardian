# AI Guardian: Prompt Injection Defense System

AI Guardian demonstrates prompt injection defense for Large Language Models (LLMs). It detects and sanitizes prompt injection attacks in real time while allowing legitimate prompts to pass through.

## Interface Preview

![AI Guardian](docs/ai-guardian.png)

## Features

- **Real-time Injection Detection**: Monitors user inputs for 57 prompt injection patterns
- **Safe Pattern Recognition**: 29 safe patterns reduce false positives; safe overrides never bypass detection
- **Input Sanitization**: Redacts potentially harmful content from detected injections
- **Groq API Integration**: Uses Groq's fast inference API with multiple free-tier models
- **Welcome Banner**: First-visit splash with sample prompts to get started
- **Metrics Dashboard**: Displays total/blocked/safe attempts, average generation time; N/A when no data exists
- **Security Dashboard**: Pie and bar charts for injection overview; guidance text when empty
- **Per-Model Performance**: Sidebar tracks prompt count and average time for each model used
- **Custom Theme**: Security-themed Streamlit config (blue primary, light sidebar, sans-serif font)
- **Character Counter**: Real-time countdown with progress bar
- **Inline Clear Button**: Compact ✕ button flush with the character counter row

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
3. On first visit, see the welcome banner with sample prompts, or type your own
4. Select a model from the sidebar dropdown (defaults to Llama 3.1 8B)
5. Enter a prompt in the text area (click the ✕ button to clear)
6. Results update immediately - injection detection, sanitization, and response from the selected model
7. View metrics dashboard and security visualizations below the input
8. Track per-model performance in the sidebar
9. Use the "Reset session" button at the bottom of the sidebar to clear all state

## Configuration

The system can be configured through the `.env` file:

- `GROQ_API_KEY`: Your Groq API key (required)

Model selection is available via the sidebar dropdown (Groq free-tier):

- **Llama 3.1 8B Instant** (default) - fast, current Groq text model
- **Llama 3.3 70B Versatile** - higher quality reasoning and longer context
- **Llama 4 Scout** - latest instruction-tuned general-purpose model
- **Qwen 3 32B** - multilingual, long-form generation

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

The system tracks two dashboards:

**Metrics Dashboard**
- **Total Attempts**: All prompt submissions (successful and blocked)
- **Blocked Threats**: Injection attempts detected and sanitized
- **Success Rate**: Ratio of safe to total attempts (shows N/A when no data)
- **Avg Generation Time**: Mean response time from the Groq API

**Security Dashboard**
- Pie chart of safe vs blocked prompts
- Bar chart of injection pattern distribution
- Both show guidance text when no data is available

## Project Structure

```
ai-guardian/
├── .streamlit/
│   └── config.toml            # Custom theme configuration
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
│   ├── test_config.py        # Configuration tests
│   ├── test_detection.py     # Detection tests
│   ├── test_model_handler.py # Handler tests
│   └── test_state.py         # State tests
├── .env / .env.example       # Configuration
└── pyproject.toml            # Project metadata & dependencies
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
