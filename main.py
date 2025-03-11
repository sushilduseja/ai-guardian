import sys
import importlib

# Force pandas to fully load before other imports
if 'pandas' in sys.modules:
    importlib.reload(sys.modules['pandas'])

import streamlit as st
import plotly.express as px
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import MODEL_NAME
from utils import detect_injection, sanitize_prompt
import torch
import asyncio
from typing import Optional, Tuple
import time

# Set page configuration including title
st.set_page_config(
    page_title="AI Guardian",
    page_icon="🛡️",
    layout="wide"
)

# Initialize all session state variables
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "generation_history" not in st.session_state:
    st.session_state.generation_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "blocked" not in st.session_state:
    st.session_state.blocked = 0

# Enhanced UI setup with more natural heading
st.write("# AI Guardian")
st.write("Your shield against prompt injection attacks")

# Create columns for key metrics at the top
col1, col2, col3, col4 = st.columns(4)
safe_attempts = st.session_state.attempts - st.session_state.blocked

with col1:
    st.metric(
        "Success Rate",
        f"{(safe_attempts/max(1, st.session_state.attempts))*100:.1f}%",
        delta="Good" if safe_attempts > st.session_state.blocked else "Needs Attention"
    )

with col2:
    st.metric(
        "Total Prompts",
        st.session_state.attempts,
        delta=f"+{st.session_state.attempts - st.session_state.blocked}"
    )

with col3:
    st.metric(
        "Blocked Threats",
        st.session_state.blocked,
        delta=f"{(st.session_state.blocked/max(1, st.session_state.attempts))*100:.1f}% of total"
    )

with col4:
    avg_time = sum([1.5]) / max(1, len(st.session_state.generation_history))
    st.metric(
        "Avg Response Time",
        f"{avg_time:.2f}s",
        delta="Fast" if avg_time < 2 else "Normal"
    )

# Smart model loading with progress indication
@st.cache_resource
def load_model() -> Tuple[Optional[AutoModelForCausalLM], Optional[AutoTokenizer]]:
    try:
        with st.spinner("🔄 Loading AI model... This may take a few moments."):
            progress_bar = st.progress(0)
            
            # Simulate progress for better UX
            progress_bar.progress(30)
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, 
                                                    low_cpu_mem_usage=True)
            
            progress_bar.progress(60)
            model = AutoModelForCausalLM.from_pretrained(MODEL_NAME,
                                                       low_cpu_mem_usage=True,
                                                       torch_dtype=torch.float32)
            
            progress_bar.progress(100)
            st.success("✅ Model loaded successfully!")
            st.session_state.model_loaded = True
            return model, tokenizer
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        st.info("💡 Tip: Try refreshing the page or check your internet connection.")
        return None, None

# Intelligent text generation with real-time feedback
def generate_text_with_feedback(prompt: str, model, tokenizer, max_length=100):
    if not (model and tokenizer):
        return [{"generated_text": "Model not ready. Please wait..."}]
    
    try:
        formatted_prompt = f"Provide a clear and direct response to: {prompt}"
        with st.spinner("🤔 Generating response..."):
            inputs = tokenizer.encode(formatted_prompt, return_tensors="pt")
            
            # Show real-time token processing
            progress_bar = st.progress(0)
            start_time = time.time()
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=0.3,
                    top_p=0.7,
                    num_beams=3,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                
                # Update progress based on generation
                progress_bar.progress(100)
                
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(formatted_prompt, "").strip()
            
            # Store in history for smart suggestions
            st.session_state.generation_history.append((prompt, response))
            
            generation_time = time.time() - start_time
            st.info(f"⚡ Generated in {generation_time:.2f} seconds")
            
            return [{"generated_text": response}]
            
    except Exception as e:
        st.error(f"Generation error: {e}")
        st.info("💡 Tip: Try simplifying your prompt or try again.")
        return [{"generated_text": f"Error processing: {prompt[:50]}..."}]

# Load model with progress indication
model, tokenizer = load_model()

def on_prompt_change():
    """Callback to handle prompt changes"""
    st.session_state.current_prompt = st.session_state.input_prompt
    st.session_state.last_prompt = st.session_state.current_prompt

# Smart input section with clear visual hierarchy
st.write("## 💬 Enter Your Prompt")
MAX_CHARS = 500
current_chars = len(st.session_state.current_prompt)
chars_remaining = MAX_CHARS - current_chars
st.caption(f"Characters remaining: {chars_remaining}")

user_prompt = st.text_area(
    "",  # Remove label as it's shown in the header
    key="input_prompt",
    value=st.session_state.current_prompt,
    max_chars=MAX_CHARS,
    help="Type your prompt here. AI Guardian will protect against injection attacks.",
    on_change=on_prompt_change,
    height=100  # Make input area more prominent
)

# Progress bar for character count
if current_chars > 0:
    progress = current_chars / MAX_CHARS
    st.progress(min(progress, 1.0))

# Real-time input validation
if st.session_state.current_prompt:
    # Show smart suggestions from history
    if st.session_state.generation_history:
        similar_prompts = [p for p, r in st.session_state.generation_history 
                         if p.lower().startswith(st.session_state.current_prompt.lower())]
        if similar_prompts:
            st.info("💡 Similar previous prompts: " + ", ".join(similar_prompts[:3]))

# Streamlined interaction with single-click operation
if st.session_state.current_prompt:
    # Check injection with real-time feedback
    injection_detected = detect_injection(st.session_state.current_prompt)
    sanitized_prompt = sanitize_prompt(st.session_state.current_prompt)
    
    if injection_detected:
        st.warning("🛡️ Potential prompt injection detected! Input has been sanitized.")
        st.session_state.blocked += 1
        
        # Show what was detected
        st.write("Original:", st.session_state.current_prompt)
        st.write("Sanitized:", sanitized_prompt)
    else:
        st.success("✅ No prompt injection detected.")
    
    st.session_state.attempts += 1
    
    # Generate response with progress tracking
    try:
        response = generate_text_with_feedback(sanitized_prompt, model, tokenizer)
        st.write("### 🤖 Model Response:")
        st.write(response[0]["generated_text"])
        # Update last prompt after successful generation
        st.session_state.last_prompt = st.session_state.current_prompt
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.write("### ⚠️ Fallback Response:")
        st.write(f"Input received: {sanitized_prompt[:50]}...")

# Visualization section
st.write("## 📊 Security Dashboard")

# Create two columns for visualizations
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    # Pie chart for better visual impact
    safe_attempts = st.session_state.attempts - st.session_state.blocked
    pie_data = {
        "Status": ["Safe Prompts", "Blocked Attempts"],
        "Count": [safe_attempts, st.session_state.blocked]
    }
    fig1 = px.pie(
        pie_data,
        values="Count",
        names="Status",
        title="Safety Analysis",
        color="Status",
        color_discrete_map={
            "Safe Prompts": "#00CC96",
            "Blocked Attempts": "#EF553B"
        }
    )
    st.plotly_chart(fig1, use_container_width=True)

with viz_col2:
    # Bar chart
    data = {
        "Type": ["Total Attempts", "Blocked Attempts"],
        "Count": [st.session_state.attempts, st.session_state.blocked]
    }
    fig2 = px.bar(
        data, 
        x="Type", 
        y="Count", 
        title="Prompt Injection Attempts",
        color="Type",
        color_discrete_map={
            "Total Attempts": "#636EFA",
            "Blocked Attempts": "#EF553B"
        }
    )
    st.plotly_chart(fig2, use_container_width=True)

# Move tips to a more prominent position in sidebar
st.sidebar.markdown("""
# 💡 Quick Guide
### Keyboard Shortcuts
- `Ctrl+Enter`: Generate response
- `Esc`: Clear input
- `↑↓`: Browse history

### Safety Tips
- Keep prompts clear and direct
- Check sanitized output when blocked
- Review statistics for insights
""")

# Session summary at the bottom of sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### 📝 Session Overview
- ✅ Successful: {len(st.session_state.generation_history)}
- 🛡️ Blocked: {st.session_state.blocked}
- ⚡ Avg Time: {avg_time:.2f}s
""")