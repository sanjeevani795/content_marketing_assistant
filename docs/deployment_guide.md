# Deployment Guide

## Local Development
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and add API keys.
4. `streamlit run app.py`

## Hugging Face Spaces (Streamlit)
1. Create a new Space with SDK set to `Streamlit`.
2. Push this repository to the Space.
3. Ensure these files exist at repo root:
   - `app.py`
   - `requirements.txt`
4. Add secrets in Space Settings > Variables and Secrets:
   - `OPENAI_API_KEY`
   - `SERP_API_KEY` (optional)
   - `PERPLEXITY_API_KEY` (optional)
5. The app launches automatically on commit.

## HF Notes
- App entrypoint is `app.py` which imports `src/web_app/streamlit_app.py`.
- If APIs are missing, the system still works using local fallbacks.
- Keep dependency list minimal for faster cold starts.

## Production Checklist
- Enable provider fallbacks and monitor error rates.
- Add request logging with redaction for prompts containing sensitive data.
- Cache repeated research queries where possible.
