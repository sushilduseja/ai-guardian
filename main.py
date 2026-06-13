import logging
import sys
import streamlit as st
from src.config import get_api_key
from src.state import SessionState
from src.model.handler import GroqModelHandler
from src.detection import RegexSecurityChecker
from src.ui.input import create_prompt_input
from src.ui.metrics import display_metrics_dashboard
from src.ui.visualizations import create_security_dashboard
from src.ui.model_selector import select_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Guardian", page_icon="🛡️", layout="wide")


def ensure_session_state() -> SessionState:
    state = st.session_state.get("state")
    if not isinstance(state, SessionState) or not hasattr(state, "reset"):
        state = SessionState()
        st.session_state.state = state
    return state


def reset_ui_session() -> None:
    state = ensure_session_state()
    state.reset()
    st.session_state.pop("input_prompt", None)
    st.session_state.pop("prompt_input", None)
    st.rerun()

state = ensure_session_state()
logger.info("Session initialized: attempts=%d, blocked=%d", state.attempts, state.blocked)

st.write("# AI Guardian")
st.write("Your shield against prompt injection attacks")

st.sidebar.button(
    "Reset UI to initial state",
    on_click=reset_ui_session,
    help="Clear the current prompt, counters, and model session to start fresh with fewer repeated calls.",
)

security = RegexSecurityChecker()

api_key = get_api_key()
if not api_key:
    logger.error("App startup blocked: missing GROQ_API_KEY")
    st.error("GROQ_API_KEY not set. Add it to .env or set the environment variable.")
    st.stop()

selected_model = select_model()
logger.info("Model selected: %s", selected_model)

if selected_model != state.current_model:
    logger.info("Switching model: %s -> %s", state.current_model, selected_model)
    state.model_loaded = False
    state.current_model = selected_model

if not state.model_loaded:
    handler = GroqModelHandler(api_key=api_key, model=selected_model)
    state.model_loaded = True
    state.model_handler = handler
    logger.info("Model handler initialized: %s", selected_model)
elif state.model_handler is None:
    logger.error("Model handler is None despite model_loaded=True")
    st.error("Model handler not initialized")
    st.stop()
else:
    handler = state.model_handler

display_metrics_dashboard(state.safe_attempts, state.attempts, state.blocked, state.avg_generation_time)

user_prompt = create_prompt_input()

if user_prompt:
    try:
        injection_detected, sanitized_prompt = security.check_and_sanitize(user_prompt)
    except Exception as e:
        logger.error("Security check failed: %s", e, exc_info=True)
        st.error("Security analysis failed. Input was not scanned.")
        injection_detected = False
        sanitized_prompt = user_prompt

    if injection_detected:
        st.warning("🛡️ Potential prompt injection detected! Input has been sanitized.")
        state.blocked += 1
        st.write("Original:", user_prompt)
        st.write("Sanitized:", sanitized_prompt)
    else:
        st.success("✅ No prompt injection detected.")

    state.attempts += 1
    with st.spinner("🤔 Generating response..."):
        progress_bar = st.progress(0)
        try:
            response = handler.generate(sanitized_prompt)
        except Exception as e:
            logger.error("Unhandled generation exception: %s", e, exc_info=True)
            st.error(f"Generation failed: {e}")
            response = None
        progress_bar.progress(100)

    if response is not None:
        st.write("### 🤖 Model Response:")
        st.write(response.text)
        try:
            state.add_to_history(sanitized_prompt, response.text, response.generation_time)
        except ValueError as e:
            logger.error("Failed to add to history: %s", e)
        if response.status == "error":
            logger.error("Generation returned error status: %s", response.error)
            st.error(f"API Error: {response.error}")
        else:
            logger.info("Generation succeeded: model=%s, time=%.2fs, tokens=%s",
                        response.model, response.generation_time,
                        response.usage.get("total_tokens", "N/A") if response.usage else "N/A")

try:
    create_security_dashboard(state.attempts, state.blocked)
except Exception as e:
    logger.error("Failed to render security dashboard: %s", e, exc_info=True)

st.sidebar.markdown("""
# 💡 Quick Guide
### Keyboard Shortcuts
- Ctrl+Enter: Generate response
- Esc: Clear input
- ↑↓: Browse history
""")

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### 📝 Session Overview
- ✅ Successful: {len(state.generation_history)}
- 🛡️ Blocked: {state.blocked}
- ⚡ Avg Time: {state.avg_generation_time:.2f}s
""")
