import os

AVAILABLE_MODELS = {
    "distilgpt2": {
        "name": "DistilGPT2",
        "description": "Lightweight GPT2, reliable on Streamlit Cloud",
        "size": "500MB",
        "performance": "Fast",
        "use_case": "General text generation",
        "requirements": "Minimal resources"
    },
    "gpt2": {
        "name": "GPT2",
        "description": "Slightly larger GPT2 model, good performance",
        "size": "1.5GB",
        "performance": "Good",
        "use_case": "General text generation",
        "requirements": "Moderate resources"
    },
    "EleutherAI/pythia-160m": {
        "name": "Pythia 160M",
        "description": "Most efficient open source model",
        "size": "160MB",
        "performance": "Fast",
        "use_case": "Text generation",
        "requirements": "Minimal resources"
    },
    "cerebras/Cerebras-GPT-111M": {
        "name": "Cerebras GPT 111M",
        "description": "Small, efficient GPT model",
        "size": "111MB",
        "performance": "Fast",
        "use_case": "Text generation",
        "requirements": "Minimal resources"
    }
}

# Default to the most reliable model for Streamlit Cloud
DEFAULT_MODEL = "distilgpt2"

# Updated recommendations for Streamlit Cloud compatibility
RECOMMENDED_MODELS = [
    "distilgpt2",  # Most reliable
    "gpt2",  # Good balance
    "EleutherAI/pythia-160m"  # Most efficient
]

MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)

# Updated use case recommendations for Streamlit Cloud
USE_CASE_RECOMMENDATIONS = {
    "accuracy": "gpt2",
    "speed": "EleutherAI/pythia-160m",
    "balanced": "distilgpt2",
    "minimal_resources": "EleutherAI/pythia-160m",
    "cloud_deployment": "distilgpt2"
}