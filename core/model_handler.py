import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Tuple, Dict, ClassVar
import time
import logging
from contextlib import contextmanager
from .interfaces import ModelHandler, ModelResponse

logger = logging.getLogger(__name__)

@st.cache_resource
def _load_model_and_tokenizer(model_name: str) -> Tuple[Optional[AutoModelForCausalLM], Optional[AutoTokenizer]]:
    """Cached function to load model and tokenizer."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, low_cpu_mem_usage=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float32
        )
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, None

class TransformerModelHandler(ModelHandler):
    """Handles transformer model operations with proper resource management."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        
    @contextmanager
    def _progress_context(self, message: str, steps: int = 100):
        """Context manager for progress tracking."""
        with st.spinner(message):
            progress_bar = st.progress(0)
            yield lambda x: progress_bar.progress(x)
    
    def load(self) -> bool:
        """Load model with proper error handling and logging."""
        try:
            with self._progress_context("🔄 Loading AI model...") as progress:
                logger.info(f"Loading model: {self.model_name}")
                progress(30)
                
                # Use cached loader
                self.model, self.tokenizer = _load_model_and_tokenizer(self.model_name)
                if self.model is None or self.tokenizer is None:
                    raise ValueError("Failed to load model or tokenizer")
                
                progress(100)
                logger.info("Model loaded successfully")
                st.success("✅ Model loaded successfully!")
                return True
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            st.error(f"❌ Error loading model: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate response with comprehensive error handling."""
        if not (self.model and self.tokenizer):
            return ModelResponse(
                text="Model not ready. Please wait...",
                generation_time=0,
                status="error",
                error="Model not initialized"
            )
        
        try:
            formatted_prompt = f"Provide a clear and direct response to: {prompt}"
            with self._progress_context("🤔 Generating response...") as progress:
                start_time = time.time()
                
                inputs = self.tokenizer.encode(formatted_prompt, return_tensors="pt")
                progress(30)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=kwargs.get('max_length', 100),
                        temperature=kwargs.get('temperature', 0.3),
                        top_p=kwargs.get('top_p', 0.7),
                        num_beams=kwargs.get('num_beams', 3),
                        no_repeat_ngram_size=3,
                        early_stopping=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                    progress(90)
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.replace(formatted_prompt, "").strip()
                
                generation_time = time.time() - start_time
                progress(100)
                
                return ModelResponse(
                    text=response,
                    generation_time=generation_time
                )
                
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return ModelResponse(
                text=f"Error processing: {prompt[:50]}...",
                generation_time=0,
                status="error",
                error=str(e)
            )
