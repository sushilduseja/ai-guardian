import re
import logging
from utils.patterns import PROMPT_INJECTION_PATTERNS, SAFE_PATTERNS

logging.basicConfig(level=logging.INFO)

def detect_injection(prompt: str) -> bool:
    """
    Check if the prompt contains any known prompt injection patterns
    while excluding safe patterns.
    """
    # Convert to lowercase for case-insensitive matching
    prompt_lower = prompt.lower()
    
    # First check if it matches any safe patterns
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, prompt_lower):
            return False
    
    # Then check for injection patterns
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            logging.info(f"Injection pattern detected: {pattern}")
            return True
            
    return False

def sanitize_prompt(prompt: str) -> str:
    """
    Replace risky injection patterns in the prompt with a safe placeholder.
    """
    sanitized = prompt
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
    return sanitized
