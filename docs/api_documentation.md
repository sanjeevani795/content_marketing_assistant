# API Documentation (Internal)

## Query Handler Agent
- `handle_query(user_query: str, chat_history: list[dict[str, str]] | None = None) -> dict`
- Entry point for conversational requests.

## Routing
- `infer_intent(user_query: str) -> tuple[Route, dict[str, float]]`
- `route_request(user_query: str) -> Route`

## Workflow
- `run_workflow(user_query: str, chat_history: list[dict[str, str]] | None = None) -> dict`

## Specialized Agents
- Research: `run_research(query: str) -> dict`
- SEO Blog: `write_blog(topic: str, research_summary: str, keywords: list[str]) -> str`
- LinkedIn: `write_linkedin_post(topic: str, research_summary: str, include_hashtags: bool = True) -> str`
- Image: `generate_image(topic: str, brand_voice: str = "professional") -> dict`
- Strategist: `format_content_package(...) -> dict`

## Quality Pipeline
- `evaluate_outputs(outputs: dict) -> dict`
- Returns per-format scores + overall quality score + suggested improvements.
