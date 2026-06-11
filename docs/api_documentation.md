# API Documentation (Internal)

## Query Handler Agent
- `handle_query(user_query: str, chat_history: list[dict[str, str]] | None = None, prior_run: dict[str, Any] | None = None) -> dict`
- Entry point for conversational requests.
- `prior_run` enables blog and LinkedIn refinement using the previous route and generated outputs.

## Routing
- `infer_intent(user_query: str, chat_history: list[dict[str, str]] | None = None) -> tuple[Route, dict[str, float], dict[str, Any]]`
- `route_request(user_query: str, chat_history: list[dict[str, str]] | None = None) -> Route`
- Routes include `research`, `blog`, `linkedin`, `image`, and `strategy`.
- Comparison, analysis, and recommendation language contributes to research intent.
- Ambiguous requests can use recent conversation history or fall back to research.

## Workflow
- `run_workflow(user_query: str, chat_history: list[dict[str, str]] | None = None, prior_run: dict[str, Any] | None = None) -> dict`
- Returns route metadata, generated outputs, node status, execution errors, and quality analysis.

## Specialized Agents
- Research: `run_research(query: str) -> dict`
- SEO Blog: `write_blog(topic: str, research_summary: str, keywords: list[str]) -> str`
- SEO Blog refinement: `refine_blog(current_draft: str, instruction: str, topic: str, research_summary: str, keywords: list[str]) -> str`
- LinkedIn: `write_linkedin_post(topic: str, research_summary: str, include_hashtags: bool = True, instruction: str = "", reference_links: list[str] | None = None, hashtag_count: int | None = None) -> str`
- LinkedIn refinement: `refine_linkedin_post(current_draft: str, instruction: str, topic: str, research_summary: str, include_hashtags: bool = True, reference_links: list[str] | None = None, hashtag_count: int | None = None) -> str`
- Image: `generate_image(topic: str, brand_voice: str = "professional") -> dict`
- Strategist: `format_content_package(...) -> dict`

## Output Keys
- Research: `research_report`
- Blog: `research_report`, `seo_blog`
- LinkedIn: `research_report`, `linkedin_post`
- Image: `image_asset`
- Strategy: `topic`, `research_report`, `seo_blog`, `linkedin_post`, `image_asset`, `delivery_notes`

## Quality Pipeline
- `evaluate_outputs(outputs: dict, errors: list[str] | None = None) -> dict`
- Returns scores, metrics, review flags, and suggested improvements only for formats present in `outputs`, plus an overall score across those formats.
- Execution errors can reduce the overall score and add a fallback-review recommendation.
- Internal metrics remain in the workflow response for programmatic use but are not rendered as raw JSON in the Streamlit UI.

## Streamlit Presentation
- Research reports render summary, findings, sources, and provider details.
- Quality analysis renders applicable scores, review warnings, and suggested improvements.
- Raw quality metrics JSON is intentionally hidden from the user-facing output.
- Blog and LinkedIn runs support approve, revise, and reject review controls.
