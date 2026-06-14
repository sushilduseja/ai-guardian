import pytest
from src.state import SessionState


class TestSessionState:
    def test_defaults(self):
        state = SessionState()
        assert state.model_loaded is False
        assert state.generation_history == []
        assert state.attempts == 0
        assert state.blocked == 0
        assert state.current_model is None
        assert state.model_handler is None
        assert state.model_usage == {}
        assert state.show_welcome is True

    def test_show_welcome_false_after_attempt(self):
        state = SessionState(attempts=1)
        assert state.show_welcome is False

    def test_model_stats_empty_for_unknown_model(self):
        state = SessionState()
        assert state.model_stats("unknown") == {"count": 0, "total_time": 0.0}

    def test_model_stats_tracks_usage(self):
        state = SessionState()
        state.current_model = "llama-3.1-8b-instant"
        state.add_to_history("p", "r", 1.0)
        state.add_to_history("p2", "r2", 2.0)
        stats = state.model_stats("llama-3.1-8b-instant")
        assert stats["count"] == 2
        assert stats["total_time"] == 3.0

    def test_model_stats_separate_per_model(self):
        state = SessionState()
        state.current_model = "model-a"
        state.add_to_history("p", "r", 1.0)
        state.current_model = "model-b"
        state.add_to_history("p", "r", 2.0)
        assert state.model_stats("model-a")["count"] == 1
        assert state.model_stats("model-b")["count"] == 1

    def test_attempts_count(self):
        state = SessionState()
        state.attempts = 5
        state.blocked = 2
        assert state.attempts == 5
        assert state.blocked == 2

    def test_safe_attempts(self):
        state = SessionState(attempts=10, blocked=3)
        assert state.safe_attempts == 7

    def test_safe_attempts_no_blocked(self):
        state = SessionState(attempts=10, blocked=0)
        assert state.safe_attempts == 10

    def test_avg_generation_time_empty(self):
        state = SessionState()
        assert state.avg_generation_time == 0.0

    def test_avg_generation_time_single(self):
        state = SessionState()
        state.add_to_history("p", "r", 1.5)
        assert state.avg_generation_time == 1.5

    def test_avg_generation_time_multiple(self):
        state = SessionState()
        state.add_to_history("p1", "r1", 1.0)
        state.add_to_history("p2", "r2", 2.0)
        state.add_to_history("p3", "r3", 3.0)
        assert state.avg_generation_time == 2.0

    def test_add_to_history_basic(self):
        state = SessionState()
        state.add_to_history("hello", "world", 0.5)
        assert len(state.generation_history) == 1
        assert state.generation_history[0] == ("hello", "world", 0.5)

    def test_add_to_history_negative_time_raises(self):
        state = SessionState()
        with pytest.raises(ValueError, match="non-negative"):
            state.add_to_history("p", "r", -1.0)

    def test_add_to_history_trims_to_max(self):
        state = SessionState()
        for i in range(state.MAX_HISTORY + 10):
            state.add_to_history(f"p{i}", f"r{i}", float(i))
        assert len(state.generation_history) == state.MAX_HISTORY
        assert state.generation_history[0] == ("p10", "r10", 10.0)

    def test_add_to_history_under_limit_no_trim(self):
        state = SessionState()
        for i in range(state.MAX_HISTORY - 1):
            state.add_to_history(f"p{i}", f"r{i}", float(i))
        assert len(state.generation_history) == state.MAX_HISTORY - 1

    def test_reset_restores_initial_defaults(self):
        state = SessionState(
            model_loaded=True,
            generation_history=[("p", "r", 1.0)],
            attempts=5,
            blocked=2,
            current_model="llama-3.1-8b-instant",
        )

        state.reset()

        assert state.model_loaded is False
        assert state.generation_history == []
        assert state.attempts == 0
        assert state.blocked == 0
        assert state.current_model is None
        assert state.model_handler is None
        assert state.model_usage == {}
