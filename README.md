---
title: Content Marketing Assistant
emoji: "🧠"
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: "1.45.1"
app_file: src/web_app/streamlit_app.py
pinned: false
---

# Content Marketing Assistant

Multi-agent app for research and content creation (blog, LinkedIn, and image concepts) with a conversational Streamlit UI.

## What It Does
- Routes user intent to the right specialized agent
- Produces:
  - Research report
  - SEO blog draft
  - LinkedIn post draft
  - Image prompt/asset guidance
- Supports combined workflows via a content strategist
- Includes quality checks and fallback handling

## Run Locally
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env`
4. Add required secrets (at minimum `OPENAI_API_KEY`)
5. `streamlit run app.py`

## Deploy on Hugging Face Spaces
1. Create a new **Streamlit** Space
2. Push this repository
3. In Space **Settings -> Variables and secrets**, add:
   - `OPENAI_API_KEY`
   - Optional provider keys used by research/image integrations
4. Rebuild the Space

This README includes the required HF metadata block (`sdk`, `app_file`, etc.), so the Space should launch `app.py` correctly.

## Project Structure
- `src/agents/` - specialized agents
- `src/core/` - routing + workflow entrypoints
- `src/workflow/` - LangGraph state and graph assembly
- `src/integrations/` - external API clients
- `src/utils/` - quality + optimization helpers
- `src/web_app/` - Streamlit app logic
- `docs/` - architecture/deployment notes
