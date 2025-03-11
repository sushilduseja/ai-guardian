import re
import logging

logging.basicConfig(level=logging.INFO)

# List of regex patterns for common prompt injection attempts
PROMPT_INJECTION_PATTERNS = [
    # Basic patterns with flexible whitespace and punctuation
    r'ignore[\s.*,]+(?:all[\s.*,]+)?(?:previous[\s.*,]+)?instructions',
    r'disregard[\s.*,]+(?:all[\s.*,]+)?(?:previous[\s.*,]+)?instructions',
    r'override[\s.*,]+(?:all|previous)[\s.*,]+(?:commands|instructions)',
    r'bypass[\s.*,]+security[\s.*,]+checks?',
    r'ignore[\s.*,]+system[\s.*,]+prompts?',
    
    # Patterns with deliberate obfuscation
    r'i\s*g\s*n\s*o\s*r\s*e\s*.*instructions',
    r'ignore.*\n.*(?:previous|all).*\n.*instructions',
    
    # Context-aware patterns
    r'(?:first|then|later)[\s.*,]+ignore[\s.*,]+(?:previous|all)?[\s.*,]+instructions',
    r'you[\s.*,]+(?:should|must|need\s+to)[\s.*,]+ignore',
    r'do[\s.*,]+not[\s.*,]+follow[\s.*,]+(?:the[\s.*,]+)?instructions'
]

# List of safe patterns that should be preserved
SAFE_PATTERNS = [
    r'please help me understand',
    r'how do I solve this',
    r'what is the answer',
    r'can you explain'
]

def detect_injection(prompt: str) -> bool:
    """
    Check if the prompt contains any known prompt injection patterns.
    Handles complex cases including:
    - Separated characters (i g n o r e)
    - Multi-line text
    - Mixed punctuation and whitespace
    - Contextual phrases
    
    Returns True if an injection is detected.
    """
    # Normalize whitespace and line endings
    normalized_prompt = re.sub(r'\s+', ' ', prompt.lower())
    
    # First check if it's a safe pattern
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, normalized_prompt):
            return False
    
    # Then check for injection patterns
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, normalized_prompt, re.IGNORECASE | re.DOTALL):
            logging.info(f"Injection pattern detected: {pattern}")
            return True
    
    return False

def sanitize_prompt(prompt: str) -> str:
    """
    Replace risky injection patterns in the prompt with [REDACTED].
    Preserves safe patterns.
    """
    result = prompt
    
    # Don't sanitize if it matches a safe pattern exactly
    for safe_pattern in SAFE_PATTERNS:
        if re.match(f"^{safe_pattern}$", prompt.lower()):
            return prompt
    
    # Apply sanitization for injection patterns
    for pattern in PROMPT_INJECTION_PATTERNS:
        result = re.sub(pattern, "[REDACTED]", result, flags=re.IGNORECASE)
    
    return result
