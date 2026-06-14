import streamlit as st


def create_prompt_input(max_chars: int = 500):
    st.write("## 💬 Enter Your Prompt")

    user_prompt = st.text_area(
        "Prompt",
        key="input_prompt",
        value=st.session_state.get("input_prompt", ""),
        max_chars=max_chars,
        help="Type your prompt here. AI Guardian will protect against injection attacks.",
        height=100,
        label_visibility="collapsed",
    )

    def _clear_input_cb():
        st.session_state["input_prompt"] = ""

    chars_remaining = max_chars - len(user_prompt)
    caption_col, clear_col = st.columns([10, 1])
    with caption_col:
        st.caption(f"Characters remaining: {chars_remaining}")
    with clear_col:
        st.button(
            "✕",
            key="clear_prompt_button",
            help="Clear prompt",
            on_click=_clear_input_cb,
            width="stretch",
        )

    if user_prompt:
        st.progress(len(user_prompt) / max_chars)
    return user_prompt
