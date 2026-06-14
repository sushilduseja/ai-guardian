import pytest
from unittest.mock import MagicMock, patch
from src.model.handler import GroqModelHandler
from src.model.interfaces import ModelResponse


class TestGroqModelHandler:
    @pytest.fixture
    def mock_groq(self):
        import groq
        with patch("src.model.handler.groq") as mock:
            mock.RateLimitError = groq.RateLimitError
            mock.APIConnectionError = groq.APIConnectionError
            mock.APIStatusError = groq.APIStatusError

            client = MagicMock()
            mock.Groq.return_value = client

            choice = MagicMock()
            choice.message.content = "Hello, world!"

            completion = MagicMock()
            completion.choices = [choice]
            completion.model = "llama3-8b-8192"
            completion.usage = MagicMock()
            completion.usage.completion_tokens = 3
            completion.usage.prompt_tokens = 5
            completion.usage.total_tokens = 8

            client.chat.completions.create.return_value = completion
            yield mock

    def test_generate_returns_model_response(self, mock_groq):
        handler = GroqModelHandler(api_key="test-key", model="llama3-8b-8192")
        response = handler.generate("hello")

        assert isinstance(response, ModelResponse)
        assert response.text == "Hello, world!"
        assert response.model == "llama3-8b-8192"

    def test_constructor_raises_on_empty_api_key(self):
        with pytest.raises(ValueError, match="api_key is required"):
            GroqModelHandler(api_key="")

    def test_constructor_raises_on_empty_model(self):
        with pytest.raises(ValueError, match="model is required"):
            GroqModelHandler(api_key="test-key", model="")

    def test_constructor_raises_on_negative_timeout(self):
        with pytest.raises(ValueError, match="timeout must be positive"):
            GroqModelHandler(api_key="test-key", timeout=0)

    def test_constructor_raises_on_zero_timeout(self):
        with pytest.raises(ValueError, match="timeout must be positive"):
            GroqModelHandler(api_key="test-key", timeout=0)

    def test_generate_handles_rate_limit_error(self, mock_groq):
        import groq
        client = mock_groq.Groq.return_value
        client.chat.completions.create.side_effect = groq.RateLimitError(
            "rate limited", response=MagicMock(), body=None
        )

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.status == "error"
        assert "Rate limited" in response.error

    def test_generate_handles_connection_error(self, mock_groq):
        import groq
        client = mock_groq.Groq.return_value
        client.chat.completions.create.side_effect = groq.APIConnectionError(message="connection failed", request=MagicMock())

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.status == "error"
        assert "connect" in response.error.lower()

    def test_generate_handles_api_status_error(self, mock_groq):
        import groq
        client = mock_groq.Groq.return_value
        client.chat.completions.create.side_effect = groq.APIStatusError(
            "401 Unauthorized", response=MagicMock(status_code=401), body=None
        )

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.status == "error"
        assert "401" in response.error or "API error" in response.error

    def test_generate_passes_timeout_to_client(self):
        with patch("src.model.handler.groq") as mock:

            handler = GroqModelHandler(api_key="test-key", timeout=30.0)
            mock.Groq.assert_called_once_with(api_key="test-key", timeout=30.0)
    def test_generate_empty_response(self, mock_groq):
        client = mock_groq.Groq.return_value
        choice = MagicMock()
        choice.message.content = None
        completion = MagicMock()
        completion.choices = [choice]
        completion.model = "llama3-8b-8192"
        completion.usage = None
        client.chat.completions.create.return_value = completion

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.text == ""
        assert response.status == "error"

    def test_generate_usage_none_when_not_available(self, mock_groq):
        client = mock_groq.Groq.return_value
        completion = MagicMock()
        completion.choices = [MagicMock(message=MagicMock(content="hi"))]
        completion.model = "llama3-8b-8192"
        completion.usage = None
        client.chat.completions.create.return_value = completion

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.usage is None

    def test_generate_empty_choices_returns_error(self, mock_groq):
        client = mock_groq.Groq.return_value
        completion = MagicMock()
        completion.choices = []
        completion.model = "llama3-8b-8192"
        completion.usage = None
        client.chat.completions.create.return_value = completion

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.status == "error"
        assert "Empty response" in response.error

    def test_generate_null_message_returns_error(self, mock_groq):
        client = mock_groq.Groq.return_value
        choice = MagicMock()
        choice.message = None
        completion = MagicMock()
        completion.choices = [choice]
        completion.model = "llama3-8b-8192"
        completion.usage = None
        client.chat.completions.create.return_value = completion

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.status == "error"
        assert "Empty message" in response.error

    def test_extract_usage_missing_fields_uses_defaults(self, mock_groq):
        client = mock_groq.Groq.return_value
        class PartialUsage:
            pass
        completion = MagicMock()
        completion.choices = [MagicMock(message=MagicMock(content="hi"))]
        completion.model = "llama3-8b-8192"
        completion.usage = PartialUsage()
        client.chat.completions.create.return_value = completion

        handler = GroqModelHandler(api_key="test-key")
        response = handler.generate("hello")
        assert response.usage is not None
        assert response.usage["prompt_tokens"] == 0
        assert response.usage["completion_tokens"] == 0
        assert response.usage["total_tokens"] == 0
