import streamlit as st
from config import AVAILABLE_MODELS, DEFAULT_MODEL

def select_model() -> str:
    """
    Display model selection dropdown with model information.
    Returns the selected model identifier.
    """
    st.sidebar.markdown("## 🤖 Model Selection")
    
    # Create list of models with descriptions
    model_options = {f"{info['name']} - {info['description']}": model_id 
                    for model_id, info in AVAILABLE_MODELS.items()}
    
    # Get default display name
    default_display_name = next(
        name for name, id in model_options.items() 
        if id == DEFAULT_MODEL
    )
    
    # Create the selection dropdown
    selected_display = st.sidebar.selectbox(
        "Choose a model:",
        options=list(model_options.keys()),
        index=list(model_options.keys()).index(default_display_name),
        help="Select the AI model to use for generating responses"
    )
    
    selected_model = model_options[selected_display]
    
    # Show model requirements
    st.sidebar.info(
        f"ℹ️ {AVAILABLE_MODELS[selected_model]['requirements']}"
    )
    
    return selected_model
