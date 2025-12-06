```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
streamlit run web/streamlit_app.py
```

What this prototype does:
- Runs simple analyzers (flake8/bandit/eslint wrappers) if those tools are installed.
- Runs lightweight pattern heuristics to detect issues like `eval`, hardcoded secrets, missing try/except.
- Uses a deterministic, local `llm_agent` stub to produce suggested fixes and explanations (no external LLM calls).

Next steps:
- Replace the `llm_agent` stub with real LLM calls and prompt engineering.
- Improve analyzers and add caching/embeddings for example retrieval.
- Add CI and more tests.
