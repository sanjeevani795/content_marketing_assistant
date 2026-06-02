import re
from typing import Any, Literal, Optional

Route = Literal[
    "research",
    "blog",
    "linkedin",
    "image",
    "strategy",
]

ROUTE_TERMS: dict[Route, list[str]] = {
    "research": ["research", "analyze", "analysis", "sources", "competitor", "facts"],
    "blog": ["blog", "article", "seo", "long-form", "post for website"],
    "linkedin": ["linkedin", "social", "professional", "hook", "hashtags"],
    "image": ["image", "visual", "banner", "thumbnail", "poster", "graphic"],
    "strategy": ["campaign", "plan", "strategy", "all", "full", "multi-format"],
}

FOLLOW_UP_TERMS = {
    "this",
    "that",
    "it",
    "same",
    "also",
    "another",
    "again",
    "continue",
    "reuse",
    "repurpose",
    "shorter",
    "longer",
    "expand",
    "improve",
    "refine",
}

REFINEMENT_TERMS = {
    "refine",
    "rewrite",
    "revise",
    "shorten",
    "expand",
    "improve",
    "tighten",
    "polish",
    "edit",
    "rework",
    "make",
}


def _score(query: str, terms: list[str]) -> float:
    return float(sum(1 for term in terms if term in query))


def _base_scores(query: str) -> dict[Route, float]:
    q = query.lower()
    return {route: _score(q, terms) for route, terms in ROUTE_TERMS.items()}


def _apply_strategy_bonus(scores: dict[Route, float]) -> None:
    format_hits = sum(
        int(scores[route] > 0)
        for route in ("research", "blog", "linkedin", "image")
    )
    if format_hits >= 2:
        scores["strategy"] += 2.0


def _query_tokens(query: str) -> list[str]:
    return re.findall(r"[a-z0-9-]+", query.lower())


def _is_follow_up_query(query: str) -> bool:
    tokens = _query_tokens(query)
    if len(tokens) <= 4:
        return True
    return any(token in FOLLOW_UP_TERMS for token in tokens)


def is_refinement_query(query: str) -> bool:
    tokens = _query_tokens(query)
    if not tokens:
        return False
    return any(token in REFINEMENT_TERMS for token in tokens) and any(
        token in {"this", "that", "post", "blog", "article", "draft", "it", "copy", "version", "shorter", "longer", "punchier", "clearer", "stronger"}
        for token in tokens
    )


def _is_ambiguous(query: str, scores: dict[Route, float]) -> bool:
    ordered_scores = sorted(scores.values(), reverse=True)
    top_score = ordered_scores[0]
    second_score = ordered_scores[1]
    short_query = len(_query_tokens(query)) <= 6

    return bool(
        top_score == 0
        or (short_query and top_score <= 1.0 and (top_score - second_score) <= 0.5)
    )


def _prior_user_messages(
    chat_history: Optional[list[dict[str, str]]], current_query: str
) -> list[str]:
    if not chat_history:
        return []

    prior_messages: list[str] = []
    skipped_current = False
    for turn in reversed(chat_history):
        if turn.get("role") != "user":
            continue

        content = turn.get("content", "").strip()
        if not content:
            continue

        if not skipped_current and content == current_query.strip():
            skipped_current = True
            continue

        prior_messages.append(content)

    prior_messages.reverse()
    return prior_messages


def _history_scores(
    chat_history: Optional[list[dict[str, str]]], current_query: str
) -> dict[Route, float]:
    scores: dict[Route, float] = {route: 0.0 for route in ROUTE_TERMS}
    prior_messages = _prior_user_messages(chat_history, current_query)

    for index, message in enumerate(reversed(prior_messages[-3:]), start=1):
        weight = max(0.25, 0.8 - (index - 1) * 0.2)
        message_scores = _base_scores(message)
        _apply_strategy_bonus(message_scores)
        for route, value in message_scores.items():
            scores[route] += value * weight

    return scores


def _last_assistant_route(chat_history: Optional[list[dict[str, str]]]) -> Optional[Route]:
    if not chat_history:
        return None

    pattern = re.compile(r"`(research|blog|linkedin|image|strategy)`")
    for turn in reversed(chat_history):
        if turn.get("role") != "assistant":
            continue
        match = pattern.search(turn.get("content", ""))
        if match:
            return match.group(1)  # type: ignore[return-value]

    return None


def build_topic(user_query: str, chat_history: Optional[list[dict[str, str]]] = None) -> str:
    prior_messages = _prior_user_messages(chat_history, user_query)
    if not prior_messages:
        return user_query

    if _is_follow_up_query(user_query):
        return (
            f"Original topic context: {prior_messages[-1]}\n"
            f"Follow-up request: {user_query}"
        )

    return user_query


def infer_intent(
    user_query: str, chat_history: Optional[list[dict[str, str]]] = None
) -> tuple[Route, dict[str, float], dict[str, Any]]:
    current_scores = _base_scores(user_query)
    _apply_strategy_bonus(current_scores)
    scores = current_scores.copy()
    ambiguous = _is_ambiguous(user_query, current_scores)
    history_used = False
    history_scores: dict[Route, float] = {route: 0.0 for route in ROUTE_TERMS}
    last_route = _last_assistant_route(chat_history)

    if chat_history and ambiguous:
        history_scores = _history_scores(chat_history, user_query)
        for route, value in history_scores.items():
            scores[route] += round(value * 0.6, 2)
        if last_route:
            scores[last_route] += 0.75
        history_used = True

    route: Route = max(scores, key=scores.get)
    route_source = "query"

    if ambiguous and history_used and (history_scores[route] > 0 or last_route == route):
        route_source = "history_fallback"
    elif ambiguous:
        route = "research"
        route_source = "ambiguity_fallback"

    return route, scores, {
        "ambiguous": ambiguous,
        "history_used": history_used,
        "history_scores": history_scores,
        "current_scores": current_scores,
        "last_route": last_route,
        "route_source": route_source,
    }


def route_request(
    user_query: str, chat_history: Optional[list[dict[str, str]]] = None
) -> Route:
    route, _, _ = infer_intent(user_query, chat_history=chat_history)
    return route
