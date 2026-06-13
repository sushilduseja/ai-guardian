import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

AVAILABLE_MODELS = {
    "llama-3.1-8b-instant": {
        "name": "Llama 3.1 8B Instant",
        "description": "Fast, current Groq text model for everyday prompts",
        "provider": "Groq",
        "use_case": "General text generation",
    },
    "llama-3.3-70b-versatile": {
        "name": "Llama 3.3 70B Versatile",
        "description": "Higher quality reasoning with longer context",
        "provider": "Groq",
        "use_case": "Reasoning and complex tasks",
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "name": "Llama 4 Scout",
        "description": "Latest instruction-tuned Groq model for strong general performance",
        "provider": "Groq",
        "use_case": "Instruction following",
    },
    "qwen/qwen3-32b": {
        "name": "Qwen 3 32B",
        "description": "High-capacity multilingual model for broad text tasks",
        "provider": "Groq",
        "use_case": "Multilingual and long-form generation",
    },
}

DEFAULT_MODEL = "llama-3.1-8b-instant"

_env_loaded: bool = False


def get_api_key() -> str:
    global _env_loaded
    if not _env_loaded:
        try:
            loaded = load_dotenv()
            if loaded:
                logger.info("Loaded .env file: %s", loaded)
            else:
                logger.info("No .env file found, using environment variables")
        except Exception as e:
            logger.warning("Failed to load .env file: %s", e)
        _env_loaded = True
    try:
        key = os.getenv("GROQ_API_KEY", "")
    except Exception as e:
        logger.error("Failed to read GROQ_API_KEY: %s", e)
        return ""
    if not key:
        logger.warning("GROQ_API_KEY not found in environment")
    else:
        logger.info("GROQ_API_KEY loaded (%d chars)", len(key))
    return key
