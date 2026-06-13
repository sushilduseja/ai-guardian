import streamlit as st
import streamlit.components.v1 as components


def create_prompt_input(max_chars: int = 500):
    st.write("## 💬 Enter Your Prompt")

    # If the page was invoked with ?clear_prompt=1, clear the stored
    # prompt before creating the textarea widget (safe to mutate here).
    if st.query_params.get("clear_prompt"):
        st.session_state["input_prompt"] = ""
        # Remove the query param so subsequent runs are clean.
        st.query_params.clear()
    # Render the prompt header row with a right-aligned clear icon
    header_left, header_right = st.columns([9, 1])
    with header_left:
        # empty to keep alignment; could place a sublabel here in future
        st.markdown("&nbsp;", unsafe_allow_html=True)

    def _clear_input_cb():
        # Callback runs before the rest of the widgets are created
        # in this script run, so it's safe to mutate session state here.
        st.session_state["input_prompt"] = ""

    with header_right:
        # Compact icon-style button aligned to the right of the text area
        st.button(
            "✕",
            key="clear_prompt_button",
            help="Clear the typed prompt",
            on_click=_clear_input_cb,
            use_container_width=True,
        )

    # Instantiate the text area using the current session value (may be
    # set to empty by the callback above when the clear icon is clicked).
    user_prompt = st.text_area(
        "Prompt",
        key="input_prompt",
        value=st.session_state.get("input_prompt", ""),
        max_chars=max_chars,
        help="Type your prompt here. AI Guardian will protect against injection attacks.",
        height=100,
        label_visibility="collapsed",
    )

    # Inject a tiny script that overlays a clear icon inside the textarea
    # container. Clicking it navigates to ?clear_prompt=1 which the code
    # above will pick up on the next run and safely clear the widget.
    overlay_js = f"""
    <style>
    .streamlit-clear-overlay {{
        position: absolute;
        right: 18px;
        top: 12px;
        z-index: 9999;
        background: #ffffff;
        border-radius: 50%;
        border: 1px solid rgba(0,0,0,0.12);
        width: 28px; height: 28px;
        display:flex; align-items:center; justify-content:center;
        font-weight:600; cursor:pointer; box-shadow:0 1px 3px rgba(0,0,0,0.12);
    }}
    </style>
    <script>
    (function(){{
        function placeIcon(){{
            var textarea = document.querySelector('textarea[aria-label="Prompt"]');
            if(!textarea) return false;
            // find an ancestor container to attach absolute-positioned icon
            var container = textarea.closest('.stTextArea') || textarea.parentElement;
            if(!container) container = textarea.parentElement;
            // ensure container is positioned
            container.style.position = 'relative';
            if (container.querySelector('.streamlit-clear-overlay')) return true;
            var icon = document.createElement('a');
            icon.className = 'streamlit-clear-overlay';
            icon.href = (window.location.pathname || '') + '?clear_prompt=1';
            icon.title = 'Clear prompt';
            icon.innerHTML = '✕';
            container.appendChild(icon);
            return true;
        }}
        if(!placeIcon()){{
            var tries=0; var id=setInterval(function(){{ if(placeIcon()||tries++>30) clearInterval(id); }},100);
        }} )();
    </script>
    """
    try:
        components.html(overlay_js, height=0)
    except Exception:
        # If components are not available in some runtimes, silently ignore
        pass

    chars_remaining = max_chars - len(user_prompt)
    st.caption(f"Characters remaining: {chars_remaining}")
    if user_prompt:
        st.progress(len(user_prompt) / max_chars)
    return user_prompt
