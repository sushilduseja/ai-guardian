"""
AI Guardian: Prompt Injection Defense System

This application demonstrates different types of prompt injection attacks
and implements multiple defense strategies to prevent these attacks.
"""
import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

import openai
import anthropic
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate

from config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_DEFENSE_STRATEGIES,
    PAGE_TITLE,
    PAGE_ICON,
    HUGGINGFACE_FALLBACK_MODEL,
    ENABLE_FALLBACK,
    check_api_keys
)
from utils.attacks import AttackDetector, get_educational_examples
from utils.defenses import get_available_defenses
from utils.detection import analyze_response, evaluate_defense_effectiveness
from utils.visualization import (
    create_attack_detection_chart,
    create_defense_effectiveness_chart,
    create_confidence_reduction_chart,
    create_attack_success_timeline
)


# Initialize session state for storing history
def init_session_state():
    """Initialize Streamlit session state variables."""
    if "detection_history" not in st.session_state:
        st.session_state.detection_history = []
    
    if "effectiveness_history" not in st.session_state:
        st.session_state.effectiveness_history = []
    
    if "prompt_history" not in st.session_state:
        st.session_state.prompt_history = []


# Configure API clients
def configure_api_client(provider: str):
    """
    Configure the API client for the selected provider.
    
    Args:
        provider: The LLM provider ("openai" or "anthropic")
        
    Returns:
        Configured API client
    """
    if provider == "openai":
        if not OPENAI_API_KEY:
            st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            st.stop()
        
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        return openai_client
    
    elif provider == "anthropic":
        if not ANTHROPIC_API_KEY:
            st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
            st.stop()
        
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return anthropic_client
    
    else:
        st.error(f"Unsupported provider: {provider}")
        st.stop()


# Generate response from the LLM
def generate_response(prompt: str, model: str, provider: str) -> str:
    """
    Generate a response from the selected LLM with fallback to open-source models.
    
    Args:
        prompt: The prompt to send to the model
        model: The model identifier
        provider: The LLM provider
        
    Returns:
        The model's response text
    """
    try:
        if provider == "openai":
            try:
                client = configure_api_client("openai")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except (openai.RateLimitError, openai.APIConnectionError) as e:
                st.warning(f"OpenAI API limit reached or connection error: {str(e)}")
                if ENABLE_FALLBACK:
                    st.info("Falling back to open-source Hugging Face model...")
                    return generate_huggingface_response(prompt)
                else:
                    return f"Error: API limit exceeded. Enable fallback or try again later."
        
        elif provider == "anthropic":
            try:
                client = configure_api_client("anthropic")
                response = client.messages.create(
                    model=model,
                    max_tokens=1000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except (anthropic.RateLimitError, anthropic.APIConnectionError) as e:
                st.warning(f"Anthropic API limit reached or connection error: {str(e)}")
                if ENABLE_FALLBACK:
                    st.info("Falling back to open-source Hugging Face model...")
                    return generate_huggingface_response(prompt)
                else:
                    return f"Error: API limit exceeded. Enable fallback or try again later."
        
        elif provider == "huggingface":
            return generate_huggingface_response(prompt)
        
        else:
            return f"Error: Unsupported provider {provider}"
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_huggingface_response(prompt: str) -> str:
    """Generate a response using a Hugging Face model."""
    try:
        from transformers import pipeline
        
        # Initialize pipeline with smaller, freely available model
        generator = pipeline(
            "text-generation",
            model=HUGGINGFACE_FALLBACK_MODEL,
            device_map="auto",
            model_kwargs={"torch_dtype": "auto"}
        )
        
        # Add truncation parameter to fix warning
        response = generator(
            prompt,
            max_length=512,
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
            num_return_sequences=1,
            return_full_text=False,
            truncation=True  # Added this parameter
        )
        
        return response[0]["generated_text"].strip()
    
    except Exception as e:
        st.error(f"Error with Hugging Face fallback model: {str(e)}")
        return "Error: Could not generate response using fallback model. Please try again or use a different provider."

# Apply selected defense strategies
def apply_defenses(prompt: str, selected_defenses: List[str]) -> Tuple[str, Dict]:
    """
    Apply selected defense strategies to the prompt.
    
    Args:
        prompt: The original prompt
        selected_defenses: List of defense strategy names to apply
        
    Returns:
        Tuple of (defended prompt, defense metadata)
    """
    available_defenses = get_available_defenses()
    
    if "composite" in selected_defenses:
        # Use the pre-configured composite defense
        defended_prompt, metadata = available_defenses["composite"].defend(prompt)
    else:
        # Apply selected defenses in sequence
        current_prompt = prompt
        all_metadata = []
        
        for defense_name in selected_defenses:
            if defense_name in available_defenses:
                current_prompt, metadata = available_defenses[defense_name].defend(current_prompt)
                all_metadata.append(metadata)
        
        defended_prompt = current_prompt
        metadata = {
            "strategy": "custom_composite",
            "individual_strategies": all_metadata,
            "modified": any(m["modified"] for m in all_metadata),
            "original_length": len(prompt),
            "new_length": len(defended_prompt)
        }
    
    return defended_prompt, metadata


def main():
    """Main application function."""
    # Set up page config
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    provider = st.sidebar.selectbox(
        "Select LLM Provider",
        ["openai", "anthropic", "huggingface"],
        index=0
    )
    
    # Model selection based on provider
    if provider == "openai":
        model = st.sidebar.selectbox(
            "Select Model",
            ["gpt-3.5-turbo", "gpt-4"],
            index=0
        )
    elif provider == "anthropic":
        model = st.sidebar.selectbox(
            "Select Model",
            ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            index=2
        )
    else:
        model = HUGGINGFACE_FALLBACK_MODEL
    
    # Defense strategy selection
    available_defenses = list(get_available_defenses().keys())
    selected_defenses = st.sidebar.multiselect(
        "Select Defense Strategies",
        available_defenses,
        default=DEFAULT_DEFENSE_STRATEGIES
    )
    
    # Main interaction area
    st.header("Prompt Testing Area")
    
    user_prompt = st.text_area("Enter your prompt:", height=100)
    
    if st.button("Test Prompt"):
        if not user_prompt:
            st.warning("Please enter a prompt to test.")
            return
        
        if not check_api_keys(provider):
            st.error(f"Missing API key for {provider}. Please check your configuration.")
            return
        
        with st.spinner("Processing..."):
            # Apply selected defenses
            defended_prompt, defense_metadata = apply_defenses(user_prompt, selected_defenses)
            
            # Generate responses
            original_response = generate_response(user_prompt, model, provider)
            defended_response = generate_response(defended_prompt, model, provider)
            
            # Analyze responses
            original_analysis = analyze_response(user_prompt, original_response)
            defense_evaluation = evaluate_defense_effectiveness(
                user_prompt, 
                defended_prompt,
                original_response,
                defended_response
            )
            
            # Update history
            st.session_state.detection_history.append(original_analysis)
            st.session_state.effectiveness_history.append({
                **defense_evaluation,
                "strategy": ",".join(selected_defenses)
            })
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original Prompt")
                st.text_area("Original prompt content", user_prompt, height=100, disabled=True)
                st.subheader("Original Response")
                st.text_area("Original response content", original_response, height=200, disabled=True)
            
            with col2:
                st.subheader("Defended Prompt")
                st.text_area("Defended prompt content", defended_prompt, height=100, disabled=True)
                st.subheader("Defended Response")
                st.text_area("Defended response content", defended_response, height=200, disabled=True)
            
            # Display analysis
            st.header("Analysis Results")
            
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric(
                    "Attack Success Likelihood",
                    f"{original_analysis['confidence']:.2%}"
                )
            
            with metrics_col2:
                st.metric(
                    "Defense Effectiveness",
                    "Effective" if defense_evaluation["defense_effective"] else "Ineffective"
                )
            
            with metrics_col3:
                st.metric(
                    "Confidence Reduction",
                    f"{defense_evaluation['confidence_reduction']:.2%}"
                )
    
    # Visualization section
    st.header("Analysis Dashboard")
    
    if st.session_state.detection_history:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_attack_detection_chart(st.session_state.detection_history),
                use_container_width=True
            )
            st.plotly_chart(
                create_defense_effectiveness_chart(st.session_state.effectiveness_history),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_confidence_reduction_chart(st.session_state.effectiveness_history),
                use_container_width=True
            )
            st.plotly_chart(
                create_attack_success_timeline(st.session_state.detection_history),
                use_container_width=True
            )
    else:
        st.info("No analysis data available yet. Test some prompts to see visualizations.")

# Entry point
if __name__ == "__main__":
    main()