# AI Guardian — Domain Context

## What is AI Guardian?

A Streamlit-based demonstration system that detects and sanitizes prompt injection attacks against LLMs in real time. Users type prompts, the system checks for injection patterns, sanitizes if needed, then forwards the sanitized prompt to a Groq API model for text generation.

---

## Architecture overview

```
main.py                           ← Streamlit entry point
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
    ├── input.py                  ← prompt text area with character counter
    ├── metrics.py                ← 4-column KPI dashboard (Streamlit metrics)
    ├── visualizations.py         ← Plotly pie/bar charts for security analytics
    └── model_selector.py         ← sidebar dropdown to pick Groq model
tests/
├── test_detection.py             ← RegexSecurityChecker unit tests
├── test_model_handler.py         ← GroqModelHandler unit tests (mocked)
└── test_state.py                 ← SessionState unit tests
.env                              ← GROQ_API_KEY (gitignored)
.env.example                      ← template (committed)
```

## Flow

1. User selects a model via sidebar dropdown → config lookup → `GroqModelHandler(api_key, model)`
2. User enters prompt in text area → character counter tracks room
3. `security.check(prompt)` runs `RegexSecurityChecker` against comprehensive injection pattern catalog
4. If injection detected → `security.sanitize()` replaces matched regions with `[REDACTED]`
5. `handler.generate(sanitized_prompt)` → Groq API chat completion → response displayed
6. Metrics dashboard (success rate, total, blocked, avg time from real generation times) + Plotly visualizations update

---

## Glossary

| Term | Meaning |
|---|---|
| **prompt injection** | An attack where user input tricks an LLM into overriding its system instructions |
| **sanitization** | Replacing detected injection patterns with `[REDACTED]` before forwarding to the model |
| **detection** | Boolean check — does the prompt match any `INJECTION_PATTERNS`? |
| **safe pattern** | A regex that looks like an injection but isn't — short-circuits detection |
| **blocked** | Counter of prompts flagged as injections |
| **attempts** | Total prompts submitted (successful + blocked) |
| **ModelHandler** | Abstract interface for generating text via an LLM |
| **GroqModelHandler** | Concrete `ModelHandler` using the Groq API |
| **ModelResponse** | Dataclass with text, generation_time, status, error, model, usage |
| **SecurityChecker** | Abstract interface for checking and sanitizing prompts |
| **RegexSecurityChecker** | Concrete `SecurityChecker` using regex pattern matching |
| **SessionState** | Dataclass bundling all Streamlit session state |

## Architecture decisions

### Groq API replaces local Hugging Face models
Running `distilgpt2`/`gpt2` locally required PyTorch and several GB of dependencies — impractical for Streamlit Cloud and slow on modest hardware. The Groq API provides near-instant inference on Llama 3 / Mixtral / Gemma 2 without local GPU requirements.

### SecurityChecker seam with one adapter
The `SecurityChecker` ABC defines the seam; `RegexSecurityChecker` is the sole production adapter. A second adapter (e.g. `AlwaysPassSecurityChecker` for tests) would make the seam "real" per the two-adapter rule.

### SessionState dataclass consolidates all Streamlit state
Previously 6 raw `st.session_state` keys scattered across `main.py`. Now one `SessionState` dataclass with typed fields and defaults.

### Real generation time tracking
`ModelResponse.generation_time` is captured at the API call site in `GroqModelHandler`, stored in `generation_history`, and averaged for the metrics display.

## Dead code removed

- `utils/patterns.py` — abandoned refactor, patterns consolidated into `src/detection.py`
- `utils/utils.py` — thin wrapper, folded into direct `RegexSecurityChecker` usage
- `core/` and `components/` — flattened into `src/` package
- `TransformerModelHandler` — removed with Hugging Face → Groq migration
