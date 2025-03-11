import unittest
from unittest.mock import Mock, patch
import sys

# Create mock modules
mock_modules = {
    'torch': Mock(),
    'transformers': Mock(),
    'transformers.AutoModelForCausalLM': Mock(),
    'transformers.AutoTokenizer': Mock()
}

# Apply mocks before any imports
for mod_name, mock in mock_modules.items():
    sys.modules[mod_name] = mock

# Now import our modules
from core.interfaces import ModelResponse

class MockModelHandler:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None

    def load(self):
        return True

    def generate(self, prompt, **kwargs):
        return ModelResponse(
            text="Test response",
            generation_time=0.1,
            status="success"
        )

class TestModelHandler(unittest.TestCase):
    """Test suite for model handling."""
    
    def setUp(self):
        self.model_name = "test-model"
        self.handler = MockModelHandler(self.model_name)
    
    def test_basic_generation(self):
        """Test basic text generation."""
        response = self.handler.generate("Test prompt")
        self.assertEqual(response.status, "success")
        self.assertIsInstance(response.text, str)
        self.assertIsInstance(response.generation_time, float)
    
    def test_error_handling(self):
        """Test error handling during generation."""
        handler = MockModelHandler(None)
        handler.model = None
        handler.tokenizer = None
        
        response = handler.generate("Test prompt")
        self.assertIsInstance(response, ModelResponse)
    
    def test_generation_parameters(self):
        """Test generation with different parameters."""
        response = self.handler.generate(
            "Test prompt",
            temperature=0.5,
            max_length=200,
            top_p=0.8
        )
        self.assertEqual(response.status, "success")

if __name__ == '__main__':
    unittest.main()
