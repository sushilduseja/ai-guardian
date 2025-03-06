import streamlit as st
import plotly.express as px
from transformers import pipeline
from config import MODEL_NAME
from utils import detect_injection, sanitize_prompt

# Set up the Streamlit app title and description.
st.write("# AI Guardian: Prompt Injection Defense System")
st.write("This demo showcases prompt injection defense techniques.")

# Load the Hugging Face text generation model.
try:
    generator = pipeline("text-generation", MODEL_NAME)
except Exception as e:
    st.error(f"Error loading model: {e}")
    generator = None

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
            response = generator(sanitized_prompt, max_length=100, do_sample=True)
            st.write("### Model Response:")
            st.write(response[0]["generated_text"])
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.error("Please enter a prompt.")

# Visualization: Bar chart showing statistics.
st.write("## Attack Attempt Statistics")
data = {
    "Type": ["Total Attempts", "Blocked Attempts"],
    "Count": [st.session_state.attempts, st.session_state.blocked]
}
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
