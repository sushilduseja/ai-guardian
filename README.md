# AI Guardian: Prompt Injection Defense System

AI Guardian is a robust tool designed to detect, analyze, and mitigate prompt injection attacks targeting Large Language Models (LLMs). It offers a multi-layered defense approach, real-time analysis, and an interactive dashboard to visualize attack patterns and defense effectiveness.

## 🛡️ Key Features

- **Multi-Layered Defense Strategies:**
  - Sanitization Defense: Removes known attack patterns from prompts.
  - Pattern Matching Defense: Injects warning messages into prompts containing suspicious content.
  - Prompt Structure Defense: Enforces a structured prompt format to prevent instruction overriding.
  - Composite Defense: Combines multiple defense strategies for enhanced protection.

- **Flexible LLM Provider Support:**
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - Hugging Face (Local Fallback Models)

- **Real-Time Analysis and Visualization:**
  - Attack Pattern Detection and Categorization
  - Defense Effectiveness Metrics (Success Rate, Confidence Reduction)
  - Interactive Dashboard with:
    - Attack Type Distribution Chart
    - Defense Effectiveness Chart
    - Confidence Reduction Chart
    - Attack Success Timeline

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.8+
- Git

### 2. Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/yourusername/ai-guardian.git
    cd ai-guardian
    ```

2.  Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  Configure API Keys:

    - Copy the example environment file:

      ```bash
      cp .env.example .env
      ```

    - Edit `.env` and add your API keys:

      ```
      OPENAI_API_KEY=your_openai_api_key
      ANTHROPIC_API_KEY=your_anthropic_api_key
      ```

### 3. Running the Application

```bash
streamlit run app.py
```

Open your browser and navigate to the URL provided by Streamlit (usually http://localhost:8501).

## ⚙️ Configuration

The application's behavior can be configured via `config.py`:

- **LLM Provider Settings:** Choose the default LLM provider and model.
- **Defense Strategy Settings:** Select the default defense strategies to use.
- **Hugging Face Fallback:** Enable/disable fallback to local Hugging Face models.
- **Attack Pattern Catalog:** Customize the attack patterns used for detection.

## 🛡️ Defense Strategies in Detail

1. **Sanitization Defense**
   - **Description:** Removes known prompt injection attack patterns from user input.
   - **Implementation:** Uses regular expressions and pattern matching to identify and redact malicious content.
   - **Benefits:** Reduces the likelihood of successful attacks by neutralizing common injection techniques.

2. **Pattern Matching Defense**
   - **Description:** Adds a security warning to prompts that contain suspicious patterns.
   - **Implementation:** Injects a warning message to alert the LLM to potential manipulation attempts.
   - **Benefits:** Encourages the LLM to adhere to safety guidelines and resist injection attempts.

3. **Prompt Structure Defense**
   - **Description:** Enforces a structured prompt format to isolate user input and prevent instruction overriding.
   - **Implementation:** Wraps the user's prompt within a predefined structure, providing clear boundaries and context.
   - **Benefits:** Prevents attackers from hijacking the LLM's instructions or altering its behavior.

4. **Composite Defense**
   - **Description:** Combines multiple defense strategies for layered protection.
   - **Implementation:** Applies sanitization, pattern matching, and prompt structuring in sequence.
   - **Benefits:** Provides a more robust defense against a wider range of attack techniques.

## 📊 Analysis Dashboard

The AI Guardian dashboard provides real-time insights into attack patterns and defense effectiveness:

- **Attack Type Distribution:** A bar chart showing the frequency of different attack categories.
- **Defense Effectiveness:** A stacked bar chart comparing the success and failure rates of each defense strategy.
- **Confidence Reduction:** A bar chart showing the average confidence reduction achieved by each defense strategy.
- **Attack Success Timeline:** A line chart tracking the success rate of attacks over time.

## 🧪 Testing

To run the test suite:

```bash
pytest
```

### Key test areas:

- Defense strategy effectiveness
- Attack pattern detection accuracy
- System integration and stability
- Response analysis and metric calculation## 

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.## 

## 🙏 Acknowledgments

- OpenAI, Anthropic, and Hugging Face for providing access to their LLMs.
- Streamlit for the interactive web interface.
- Plotly for the visualization tools.
- The AI safety and security community for their research and insights.

## 🔗 Related Resources
- OWASP Prompt Injection
- LangChain Documentation
- Streamlit Documentation## 

## ⚠️ Disclaimer

This tool is intended for educational and defensive purposes only. Users are responsible for complying with the terms of service and ethical guidelines of all LLM providers.