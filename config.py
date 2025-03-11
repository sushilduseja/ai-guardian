# FLAN-T5: "google/flan-t5-base" (or "google/flan-t5-large" for better performance)
# Mistral-7B-Instruct-v0.2: "mistralai/Mistral-7B-Instruct-v0.2"
# MPT-7B-Instruct: "mosaicml/mpt-7b-instruct"
# T5: "google/t5-base" (or "google/t5-small" for efficiency)
# RoBERTa: "roberta-base"
# BERT/DistilBERT: "distilbert-base-uncased"
# TinyLlama-1.1B-Chat: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# Whisper-small: "openai/whisper-small"
# "distilgpt2" (Smallest GPT2 variant, ~500MB)

import os

AVAILABLE_MODELS = {
    "distilgpt2": {
        "name": "DistilGPT2",
        "description": "Lightweight GPT2 variant (~500MB)",
        "requirements": "Minimal resources required"
    },
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0": {
        "name": "TinyLlama Chat",
        "description": "Small but effective chat model",
        "requirements": "Moderate resources required"
    },
    "google/t5-small": {
        "name": "T5 Small",
        "description": "Efficient text-to-text model",
        "requirements": "Moderate resources required"
    }
}

DEFAULT_MODEL = "distilgpt2"
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)