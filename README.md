# Content Marketing Assistant

A fully functional multi-agent content creation system with conversational UX, intelligent routing, multi-format generation, quality scoring, and Hugging Face Spaces readiness.

## Features
- Six operational agents:
  - Query Handler
  - Deep Research
  - SEO Blog Writer
  - LinkedIn Post Writer
  - Image Generation
  - Content Strategist
- Conversational Streamlit interface with multi-turn interaction.
- Multi-format output: research report, SEO blog, LinkedIn post, and image prompt/asset.
- Intent-aware routing with strategy orchestration for combined requests.
- Built-in quality analysis and optimization suggestions.
- Fallback architecture for graceful degradation when providers are unavailable.

## Quick Start
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env`
4. Add API keys (at least `OPENAI_API_KEY` for full generation).
5. `streamlit run app.py`

## Hugging Face Spaces Deployment
- Create a Streamlit Space.
- Push repo with root `app.py` and `requirements.txt`.
- Add secrets (`OPENAI_API_KEY`, optional research provider keys).
- App auto-builds and runs.

## Demo Scenarios
- Multi-turn conversational content refinement.
- Research-to-content workflow.
- Image generation with optimized prompts.
- SEO blog generation with keyword optimization.
- LinkedIn post generation with hashtag strategy.
- Error handling with provider fallback behavior.

## Project Structure
- `src/agents/`: specialized agent implementations
- `src/core/`: routing and workflow entrypoints
- `src/workflow/`: LangGraph graph and state
- `src/integrations/`: provider clients
- `src/utils/`: optimization and quality pipeline
- `src/web_app/`: Streamlit conversational interface
- `docs/`: architecture and deployment docs

## Git Remote Fix (if needed)
If push uses SSH and fails with public key errors:
- `git remote set-url origin https://github.com/sanjeevani795/content_marketing_assistant.git`
- `git push -u origin main`
