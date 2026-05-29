# Architecture Overview

## Multi-Agent System
The application uses a LangGraph workflow with six operational agents:
1. Query Handler Agent
2. Deep Research Agent
3. SEO Blog Writer Agent
4. LinkedIn Post Writer Agent
5. Image Generation Agent
6. Content Strategist Agent

## Flow
User Query -> Intent Router -> Specialized Agent Path -> Quality Validator -> Structured Outputs

## Intelligent Routing
- Intent scoring across `research`, `blog`, `linkedin`, `image`, and `strategy`.
- Multi-format requests auto-route to `strategy`, which orchestrates all content types.

## Provider Strategy
- Primary: OpenAI + SERP API.
- Secondary: Perplexity for research fallback.
- Final fallback: deterministic local generation to keep UX available.

## State and Conversation
- Workflow state tracks route, intent scores, keywords, generated artifacts, and quality signals.
- Streamlit session state stores multi-turn conversation history.
