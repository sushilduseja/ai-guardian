from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelResponse:
    text: str
    generation_time: float
    status: str = "success"
    error: str | None = None
    model: str = ""
    usage: dict | None = None


class ModelHandler(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        ...
