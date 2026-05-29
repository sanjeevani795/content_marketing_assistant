from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    user_query: str
    chat_history: list[dict[str, str]]
    route: str
    intent_scores: dict[str, float]
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
