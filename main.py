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

# Set up the Streamlit app title and description.
st.write("# AI Guardian: Prompt Injection Defense System")
st.write("This demo showcases prompt injection defense techniques.")

# Load the model and tokenizer with memory optimizations
@st.cache_resource
def load_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float32
        )
        return model, tokenizer
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None

model, tokenizer = load_model()

def generate_text(prompt, max_length=100, do_sample=True):
    if model is None or tokenizer is None:
        return [{"generated_text": f"Error: Model not loaded. Input: {prompt[:50]}..."}]
    
    try:
        # Format the prompt to be more focused and concise
        formatted_prompt = f"Please provide a direct and concise response to: {prompt}"
        inputs = tokenizer.encode(formatted_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=max_length,
                do_sample=do_sample,
                pad_token_id=tokenizer.eos_token_id,
                temperature=0.3,  # Lower temperature for more focused outputs
                top_p=0.7,       # More conservative sampling
                num_beams=3,     # Simple beam search
                no_repeat_ngram_size=3,  # Avoid repetition
                early_stopping=True
            )
        
        # Clean up the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the response if it's included
        response = response.replace(formatted_prompt, "").strip()
        
        return [{"generated_text": response}]
    except Exception as e:
        st.error(f"Generation error: {e}")
        return [{"generated_text": f"Error during generation. Input: {prompt[:50]}..."}]

# Initialize statistics in Streamlit's session state.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "blocked" not in st.session_state:
    st.session_state.blocked = 0

# Add a button to reset the statistics
if st.button("Reset Statistics"):
    st.session_state.attempts = 0
    st.session_state.blocked = 0

# User input area.
user_prompt = st.text_area("Enter your prompt:", "")

if st.button("Generate Response"):
    if user_prompt:
        # Check for potential prompt injection.
        injection_detected = detect_injection(user_prompt)
        sanitized_prompt = sanitize_prompt(user_prompt)
        
        if injection_detected:
            st.warning("Potential prompt injection detected! Input has been sanitized.")
            st.session_state.blocked += 1
        else:
            st.success("No prompt injection detected.")
        
        st.session_state.attempts += 1

        # Generate and display the response using the sanitized prompt.
        try:
            response = generate_text(sanitized_prompt, max_length=100, do_sample=True)
            st.write("### Model Response:")
            st.write(response[0]["generated_text"])
        except Exception as e:
            st.error(f"Error generating response: {e}")
            st.write("### Fallback Response:")
            st.write(f"Processed input: {sanitized_prompt[:50]}...")
    else:
        st.error("Please enter a prompt.")

# Visualization: Bar chart showing statistics.
st.write("## Attack Attempt Statistics")
data = {
    "Type": ["Total Attempts", "Blocked Attempts"],
    "Count": [st.session_state.attempts, st.session_state.blocked]
}

try:
    fig = px.bar(
        data, 
        x="Type", 
        y="Count", 
        title="Prompt Injection Attempts",
        color="Type",
        color_discrete_map={
            "Total Attempts": "#636EFA",  # Default Plotly blue
            "Blocked Attempts": "#EF553B"  # Red color
        }
    )
    st.plotly_chart(fig)
except Exception as e:
    # Fallback to simple text display
    st.error(f"Visualization error: {e}")
    st.write(f"Total Attempts: {st.session_state.attempts}")
    st.write(f"Blocked Attempts: {st.session_state.blocked}")
    
    # Even simpler fallback - create a text-based bar chart
    st.write("### Text-based Statistics:")
    st.write(f"Total Attempts: {'█' * st.session_state.attempts} ({st.session_state.attempts})")
    st.write(f"Blocked Attempts: {'█' * st.session_state.blocked} ({st.session_state.blocked})")