@echo off
echo Creating Python virtual environment with uv...
uv venv

echo Installing dependencies...
uv pip install -r requirements.txt

echo Setup complete! Activate with: .venv\Scripts\activate
echo Then run: streamlit run main.py
