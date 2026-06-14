from src.config import AVAILABLE_MODELS, DEFAULT_MODEL


def test_default_model_uses_current_groq_text_model():
    assert DEFAULT_MODEL == "llama-3.1-8b-instant"


def test_available_models_include_current_free_tier_text_models():
    model_ids = set(AVAILABLE_MODELS)

    assert "llama-3.1-8b-instant" in model_ids
    assert "llama-3.3-70b-versatile" in model_ids
    assert "meta-llama/llama-4-scout-17b-16e-instruct" in model_ids
