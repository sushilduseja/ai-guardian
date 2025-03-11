from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ModelResponse:
    """Data class for model response."""
    text: str
    generation_time: float
    status: str = "success"
    error: Optional[str] = None

class ModelHandler(ABC):
    """Abstract base class for model handling."""
    
    @abstractmethod
    def load(self) -> bool:
        """Load the model and return success status."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate response from the model."""
        pass

class SecurityChecker(ABC):
    """Abstract base class for security checking."""
    
    @abstractmethod
    def check(self, prompt: str) -> Dict[str, Any]:
        """Check prompt for security issues."""
        pass
    
    @abstractmethod
    def sanitize(self, prompt: str) -> str:
        """Sanitize the prompt."""
        pass
