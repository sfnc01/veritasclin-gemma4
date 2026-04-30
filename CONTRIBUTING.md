# Contributing to VeritasClin Field

## Setup

```bash
git clone https://github.com/<your-fork>/veritasclin-gemma4
cd veritasclin-gemma4
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your NCBI credentials; never commit .env
```

## Running the app

```bash
streamlit run app/streamlit_app.py
```

## Running tests

```bash
pytest -q -m "not integration"          # mock mode — no API keys needed
pytest -q                                # all tests — requires NCBI credentials in .env
```

## Linting

```bash
ruff check .
ruff format .
```

## LLM provider

The default provider is `mock` (no external calls). To enable Gemma 4 locally:

```bash
# Install Ollama: https://ollama.com
ollama pull gemma4:e4b
# In .env:
GEMMA_PROVIDER=ollama
```

## Secrets

**Never commit `.env`.** It is listed in `.gitignore`. If you accidentally stage it, run `git rm --cached .env` before pushing.

## Submitting a pull request

1. Fork the repo and create a feature branch.
2. Run `ruff check .` and `pytest -q -m "not integration"` — both must pass.
3. Open a PR describing what changed and why.
