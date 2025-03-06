# FLAN-T5: "google/flan-t5-base" (or "google/flan-t5-large" for better performance)
# Mistral-7B-Instruct-v0.2: "mistralai/Mistral-7B-Instruct-v0.2"
# MPT-7B-Instruct: "mosaicml/mpt-7b-instruct"
# T5: "google/t5-base" (or "google/t5-small" for efficiency)
# RoBERTa: "roberta-base"
# BERT/DistilBERT: "distilbert-base-uncased"
# TinyLlama-1.1B-Chat: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# Whisper-small: "openai/whisper-small"

import os

MODEL_NAME = os.getenv("MODEL_NAME", "google/flan-t5-large") 