import time
import logging

import groq

from .interfaces import ModelHandler, ModelResponse

logger = logging.getLogger(__name__)


class GroqModelHandler(ModelHandler):
    def __init__(self, api_key: str, model: str = "llama3-8b-8192", timeout: float = 60.0):
        if not api_key:
            raise ValueError("api_key is required")
        if not model:
            raise ValueError("model is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.model_name = model
        self._client = groq.Groq(api_key=api_key, timeout=timeout)

    def _extract_usage(self, completion) -> dict | None:
        try:
            usage = completion.usage
            if usage is None:
                return None
            return {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }
        except AttributeError:
            logger.warning("Could not extract usage from completion response")
            return None

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        start = time.time()
        try:
            completion = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 150),
                top_p=kwargs.get("top_p", 0.9),
            )
            elapsed = time.time() - start
            if not completion.choices:
                logger.error("Groq returned empty choices")
                return ModelResponse(
                    text="", generation_time=elapsed, status="error",
                    error="Empty response from API", model=self.model_name,
                )
            choice = completion.choices[0]
            if choice.message is None:
                logger.error("Groq returned choice with no message")
                return ModelResponse(
                    text="", generation_time=elapsed, status="error",
                    error="Empty message in API response", model=self.model_name,
                )
            return ModelResponse(
                text=choice.message.content or "",
                generation_time=elapsed,
                model=getattr(completion, "model", self.model_name),
                usage=self._extract_usage(completion),
            )
        except groq.RateLimitError as e:
            elapsed = time.time() - start
            logger.warning("Groq rate limited after %.2fs: %s", elapsed, e)
            return ModelResponse(
                text="", generation_time=elapsed, status="error",
                error="Rate limited. Try again later.", model=self.model_name,
            )
        except groq.APIConnectionError as e:
            elapsed = time.time() - start
            logger.error("Groq connection error after %.2fs: %s", elapsed, e)
            return ModelResponse(
                text="", generation_time=elapsed, status="error",
                error="Could not connect to Groq API. Check your network.", model=self.model_name,
            )
        except groq.APIStatusError as e:
            elapsed = time.time() - start
            logger.error("Groq API error (%s) after %.2fs: %s", e.status_code, elapsed, e)
            return ModelResponse(
                text="", generation_time=elapsed, status="error",
                error=f"API error ({e.status_code})", model=self.model_name,
            )
        except Exception as e:
            elapsed = time.time() - start
            logger.error("Groq generation error after %.2fs: %s", elapsed, e)
            return ModelResponse(
                text="",
                generation_time=elapsed,
                status="error",
                error=str(e),
                model=self.model_name,
            )
