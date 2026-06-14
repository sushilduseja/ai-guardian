# AI Guardian - Domain Context

## What is AI Guardian?

A Streamlit-based system that detects and sanitizes prompt injection attacks against LLMs in real time. Users type prompts, the system checks for injection patterns, sanitizes if needed, then forwards the sanitized prompt to a Groq API model for text generation.

---

## Architecture overview

```
main.py                           ← Streamlit entry point
.streamlit/config.toml            ← custom theme (blue primary, light sidebar)
src/                      ← app package
├── __init__.py
├── config.py                     ← Groq model registry, API key from .env
├── state.py                      ← SessionState dataclass (consolidated state)
├── detection.py                  ← SecurityChecker ABC + RegexSecurityChecker
├── model/
│   ├── __init__.py
│   ├── interfaces.py             ← ModelHandler ABC, ModelResponse dataclass
│   └── handler.py                ← GroqModelHandler (Groq API client)
└── ui/
    ├── __init__.py
    ├── input.py                  ← prompt text area with character counter + inline clear button
    ├── metrics.py                ← 4-column KPI dashboard (Streamlit metrics, N/A-safe)
    ├── visualizations.py         ← Plotly pie/bar charts for security analytics
    └── model_selector.py         ← sidebar dropdown to pick Groq model
tests/
├── test_config.py                ← Config constant tests
├── test_detection.py             ← RegexSecurityChecker unit tests
├── test_model_handler.py         ← GroqModelHandler unit tests (mocked)
└── test_state.py                 ← SessionState unit tests
.env                              ← GROQ_API_KEY (gitignored)
.env.example                      ← template (committed)
```

## Flow

1. First visit shows welcome banner with "Try sample prompt" button (prefills "What is AI Guardian...")
2. User selects a model via sidebar dropdown → config lookup → `GroqModelHandler(api_key, model)`
3. User enters prompt in text area → character counter tracks room, inline ✕ clears
4. `security.check_and_sanitize(prompt)` runs `RegexSecurityChecker` → returns `(injection_detected, sanitized_text)`
   - Injection patterns always run first; safe patterns only override detection (never bypass)
   - If injection detected → matched regions replaced with `[REDACTED]`
5. `handler.generate(sanitized_prompt)` → Groq API chat completion → `ModelResponse` with text, time, usage, status
   - Empty response or empty choices → `status="error"` (not silent success)
6. Results displayed: injection warning/clearance, model response text
7. Metrics dashboard (total, blocked, safe, avg time from real generation times) renders AFTER processing (always current)
8. Security dashboard (Plotly pie + bar charts) shows guidance text when no data yet
9. Sidebar tracks per-model performance (prompt count + avg time via `model_usage` dict)
10. Full session reset via "Reset session" button at bottom of sidebar

---

## Glossary

| Term | Meaning |
|---|---|
| **prompt injection** | An attack where user input tricks an LLM into overriding its system instructions |
| **sanitization** | Replacing detected injection patterns with `[REDACTED]` before forwarding to the model |
| **detection** | Boolean check - does the prompt match any `INJECTION_PATTERNS`? |
| **safe pattern** | A regex that looks like an injection but isn't - overrides detection result after injection patterns have already run |
| **blocked** | Counter of prompts flagged as injections |
| **attempts** | Total prompts submitted (successful + blocked) |
| **ModelHandler** | Abstract interface for generating text via an LLM |
| **GroqModelHandler** | Concrete `ModelHandler` using the Groq API |
| **ModelResponse** | Dataclass with text, generation_time, status, error, model, usage |
| **SecurityChecker** | Abstract interface with `check_and_sanitize(prompt) -> (bool, str)` |
| **RegexSecurityChecker** | Concrete `SecurityChecker` using 57 injection + 29 safe regex patterns |
| **SessionState** | Dataclass bundling all Streamlit session state, with `model_usage` dict, `model_stats()`, `show_welcome` property |

## Architecture decisions

### Groq API replaces local Hugging Face models
Running `distilgpt2`/`gpt2` locally required PyTorch and several GB of dependencies - impractical for Streamlit Cloud and slow on modest hardware. The Groq API runs Llama 3 / Mixtral / Gemma 2 without local GPU requirements.

### SecurityChecker seam with one adapter
The `SecurityChecker` ABC defines the seam; `RegexSecurityChecker` is the sole production adapter. A second adapter (e.g. `AlwaysPassSecurityChecker` for tests) would make the seam useful per the two-adapter rule.

### SessionState dataclass consolidates all Streamlit state
Previously 6 raw `st.session_state` keys scattered across `main.py`. Now one `SessionState` dataclass with typed fields and defaults.

### Real generation time tracking
`ModelResponse.generation_time` is captured at the API call site in `GroqModelHandler`, stored in `generation_history`, and averaged for the metrics display.

### Empty API response -> error status
If the Groq API returns an empty response, empty choices, or null message, the handler returns `status="error"` instead of silently returning empty string as success.

### Per-model usage tracking
`SessionState.model_usage` is a `dict[str, dict]` tracking count and total_time per model name. `add_to_history()` keys off `state.current_model`. Sidebar iterates all models with usage data plus the currently selected model.

### Metrics render after state updates
`display_metrics_dashboard()` and `create_security_dashboard()` are called after prompt processing completes, so they render current state rather than lagging one interaction behind.

### Design review decisions implemented
- `.streamlit/config.toml` for security-themed color palette instead of custom CSS
- Metrics dashboard shows N/A for zero-attempt metrics (avoiding misleading 0.00)
- Delta parameter removed from Total Prompts and Blocked Threats (semantic misuse)
- Security charts show guidance annotation when data is empty instead of hiding
- Inline clear button via Streamlit column layout (not broken JS overlay in iframe)
- Welcome banner + sample prompt for first-visit orientation

## Dead code removed

- `utils/attacks.py` - abandoned attack-pattern library, consolidated into `src/detection.py`
- `utils/defenses.py` - abandoned defense library, consolidated into `src/detection.py`
- `utils/detection.py` - abandoned detection logic, consolidated into `src/detection.py`
- `utils/visualization.py` - replaced by `src/ui/visualizations.py`
- `app.py` - renamed to `main.py` with package restructure
- `config.py` - split into `src/config.py` + `src/state.py`
- `tests/test_defenses.py` - replaced by `tests/test_detection.py` + `tests/test_model_handler.py`
