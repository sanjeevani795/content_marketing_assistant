from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    user_query: str
    chat_history: list[dict[str, str]]
    prior_route: str
    prior_outputs: dict[str, Any]
    route: str
    route_source: str
    intent_scores: dict[str, float]
    routing_details: dict[str, Any]
    ambiguity_detected: bool
    refinement_request: bool
    topic: str
    keywords: list[str]
    research: dict[str, Any]
    blog_draft: str
    linkedin_draft: str
    image_prompt: str
    image_output: str
    strategy_output: str
    quality: dict[str, Any]
    outputs: dict[str, Any]
    errors: list[str]
    node_status: dict[str, str]
