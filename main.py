import streamlit as st
from components.metrics import display_metrics_dashboard
from components.input import create_prompt_input
from components.visualizations import create_security_dashboard
from components.model_selector import select_model
from core.model_handler import TransformerModelHandler
from utils import detect_injection, sanitize_prompt

# Page configuration
st.set_page_config(
    page_title="AI Guardian",
    page_icon="🛡️",
    layout="wide"
)

# Initialize session state
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "generation_history" not in st.session_state:
    st.session_state.generation_history = []
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "blocked" not in st.session_state:
    st.session_state.blocked = 0
if "current_model" not in st.session_state:
    st.session_state.current_model = None

# App header
st.write("# AI Guardian")
st.write("Your shield against prompt injection attacks")

# Model selection
selected_model = select_model()

# Check if model needs to be reloaded
if selected_model != st.session_state.current_model:
    st.session_state.model_loaded = False
    st.session_state.current_model = selected_model

# Initialize and load model
if not st.session_state.model_loaded:
    model_handler = TransformerModelHandler(selected_model)
    model_loaded = model_handler.load()
    if model_loaded:
        st.session_state.model_loaded = True
        st.session_state.model_handler = model_handler
elif hasattr(st.session_state, 'model_handler'):
    model_handler = st.session_state.model_handler
else:
    st.error("Error: Model handler not properly initialized")
    st.stop()

# Display metrics
safe_attempts = st.session_state.attempts - st.session_state.blocked
avg_time = sum([1.5]) / max(1, len(st.session_state.generation_history))
display_metrics_dashboard(safe_attempts, st.session_state.attempts, st.session_state.blocked, avg_time)

# Get user input
user_prompt = create_prompt_input()

# Process input and generate response
if user_prompt:
    injection_detected = detect_injection(user_prompt)
    sanitized_prompt = sanitize_prompt(user_prompt)
    
    if injection_detected:
        st.warning("🛡️ Potential prompt injection detected! Input has been sanitized.")
        st.session_state.blocked += 1
        st.write("Original:", user_prompt)
        st.write("Sanitized:", sanitized_prompt)
    else:
        st.success("✅ No prompt injection detected.")
    
    st.session_state.attempts += 1
    
    response = model_handler.generate(sanitized_prompt)
    st.write("### 🤖 Model Response:")
    st.write(response.text)
    st.session_state.generation_history.append((user_prompt, response.text))

# Display visualizations
create_security_dashboard(st.session_state.attempts, st.session_state.blocked)

# Sidebar content
st.sidebar.markdown("""
# 💡 Quick Guide
### Keyboard Shortcuts
- `Ctrl+Enter`: Generate response
- `Esc`: Clear input
- `↑↓`: Browse history
""")

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### 📝 Session Overview
- ✅ Successful: {len(st.session_state.generation_history)}
- 🛡️ Blocked: {st.session_state.blocked}
- ⚡ Avg Time: {avg_time:.2f}s
""")