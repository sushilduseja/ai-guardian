import streamlit as st

def create_prompt_input(max_chars: int = 500):
    """Create and manage the prompt input area with character counter."""
    st.write("## 💬 Enter Your Prompt")
    current_chars = len(st.session_state.get("current_prompt", ""))
    chars_remaining = max_chars - current_chars
    st.caption(f"Characters remaining: {chars_remaining}")

    user_prompt = st.text_area(
        "",
        key="input_prompt",
        value=st.session_state.get("current_prompt", ""),
        max_chars=max_chars,
        help="Type your prompt here. AI Guardian will protect against injection attacks.",
        height=100
    )

    if current_chars > 0:
        progress = current_chars / max_chars
        st.progress(min(progress, 1.0))

    return user_prompt
