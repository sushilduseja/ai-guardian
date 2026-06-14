import logging
from typing import ClassVar
from dataclasses import dataclass, field

from src.model.interfaces import ModelHandler

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    MAX_HISTORY: ClassVar[int] = 100

    model_loaded: bool = False
    generation_history: list[tuple[str, str, float]] = field(default_factory=list)
    attempts: int = 0
    blocked: int = 0
    current_model: str | None = None
    model_handler: ModelHandler | None = None
    model_usage: dict[str, dict] = field(default_factory=dict)

    @property
    def safe_attempts(self) -> int:
        return self.attempts - self.blocked

    @property
    def avg_generation_time(self) -> float:
        times = [t for _, _, t in self.generation_history]
        return sum(times) / len(times) if times else 0.0

    @property
    def show_welcome(self) -> bool:
        return self.attempts == 0

    def model_stats(self, model_name: str) -> dict:
        return self.model_usage.get(model_name, {"count": 0, "total_time": 0.0})

    def reset(self) -> None:
        self.model_loaded = False
        self.generation_history = []
        self.attempts = 0
        self.blocked = 0
        self.current_model = None
        self.model_handler = None
        self.model_usage = {}
        logger.info("Session state reset to defaults")

    def add_to_history(self, prompt: str, response: str, generation_time: float) -> None:
        if generation_time < 0:
            raise ValueError("generation_time must be non-negative")
        self.generation_history.append((prompt, response, generation_time))
        if self.current_model:
            stats = self.model_usage.setdefault(self.current_model, {"count": 0, "total_time": 0.0})
            stats["count"] += 1
            stats["total_time"] += generation_time
        if len(self.generation_history) > self.MAX_HISTORY:
            removed = len(self.generation_history) - self.MAX_HISTORY
            self.generation_history = self.generation_history[-self.MAX_HISTORY:]
            logger.debug("Trimmed %d oldest entries from generation history", removed)
