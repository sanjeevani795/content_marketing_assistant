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
- Routes user intent to `research`, `blog`, `linkedin`, `image`, or a multi-format `strategy` workflow
- Treats comparison, analysis, and recommendation requests as research intent
- Uses conversation history for ambiguous follow-ups and existing drafts for blog or LinkedIn revisions
- Produces:
  - Research report
  - SEO blog draft
  - LinkedIn post draft
  - Image prompt/asset guidance
- Supports combined workflows via a content strategist
- Displays research summaries, findings, and sources in the Streamlit UI
- Scores only the content formats generated in the current run
- Shows quality scores, review warnings, and suggested improvements without exposing raw metrics JSON
- Includes provider and deterministic fallback handling

## Run Locally
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env`
4. Add required secrets (at minimum `OPENAI_API_KEY`)
5. `streamlit run app.py`

## Run Tests
`PYTHONPATH=. .venv/bin/pytest -q`

## LangSmith Observability
- Install dependencies with `pip install -r requirements.txt`
- In `.env`, set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY`
- Optional: set `LANGSMITH_PROJECT` to customize the project name
- Optional: set `LANGSMITH_ENDPOINT` if your LangSmith workspace is outside the default US region

The workflow now emits LangSmith traces for the overall run, routing, agent nodes, and raw OpenAI SDK calls when tracing is enabled.

## Deploy on Hugging Face Spaces
1. Create a new **Streamlit** Space
2. Push this repository
3. In Space **Settings -> Variables and secrets**, add:
   - `OPENAI_API_KEY`
   - Optional provider keys used by research/image integrations
4. Rebuild the Space

This README includes the required HF metadata block (`sdk`, `app_file`, etc.), so the Space launches `src/web_app/streamlit_app.py`.

## Project Structure
- `src/agents/` - specialized agents
- `src/core/` - routing + workflow entrypoints
- `src/workflow/` - LangGraph state and graph assembly
- `src/integrations/` - external API clients
- `src/utils/` - quality + optimization helpers
- `src/web_app/` - Streamlit app logic
- `docs/` - architecture/deployment notes
