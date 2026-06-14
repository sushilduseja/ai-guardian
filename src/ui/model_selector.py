import logging
import streamlit as st
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL

logger = logging.getLogger(__name__)


def select_model() -> str:
    st.sidebar.markdown("## 🤖 Model Selection")
    model_options = {}
    for model_id, info in AVAILABLE_MODELS.items():
        try:
            label = f"{info.get('name', model_id)} \u2014 {info.get('description', '')}"
            model_options[label] = model_id
        except Exception as e:
            logger.warning("Skipping model %s due to invalid config: %s", model_id, e)
            continue

    if not model_options:
        st.error("No valid models configured")
        return DEFAULT_MODEL

    keys = list(model_options.keys())
    default_display_name = DEFAULT_MODEL
    for label, mid in model_options.items():
        if mid == DEFAULT_MODEL:
            default_display_name = label
            break

    default_index = keys.index(default_display_name) if default_display_name in keys else 0
    selected_display = st.sidebar.selectbox(
        "Choose a model:",
        options=keys,
        index=default_index,
        help="Select the AI model to use for generating responses",
    )
    selected_model = model_options.get(selected_display, DEFAULT_MODEL)
    info = AVAILABLE_MODELS.get(selected_model, {})
    st.sidebar.info(f"\u2139\ufe0f {info.get('provider', 'Unknown')} \xb7 {info.get('use_case', 'General')}")
    return selected_model
