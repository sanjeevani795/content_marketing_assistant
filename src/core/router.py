from typing import Literal

Route = Literal[
    "research",
    "blog",
    "linkedin",
    "image",
    "strategy",
]


def _score(query: str, terms: list[str]) -> float:
    return float(sum(1 for term in terms if term in query))


def infer_intent(user_query: str) -> tuple[Route, dict[str, float]]:
    q = user_query.lower()
    scores = {
        "research": _score(q, ["research", "analyze", "analysis", "sources", "competitor", "facts"]),
        "blog": _score(q, ["blog", "article", "seo", "long-form", "post for website"]),
        "linkedin": _score(q, ["linkedin", "social", "professional", "hook", "hashtags"]),
        "image": _score(q, ["image", "visual", "banner", "thumbnail", "poster", "graphic"]),
        "strategy": _score(q, ["campaign", "plan", "strategy", "all", "full", "multi-format"]),
    }

    # If request asks for several formats, treat as strategy orchestration.
    format_hits = sum(
        [
            int(scores["research"] > 0),
            int(scores["blog"] > 0),
            int(scores["linkedin"] > 0),
            int(scores["image"] > 0),
        ]
    )
    if format_hits >= 2:
        scores["strategy"] += 2.0

    route = max(scores, key=scores.get)
    return route, scores


def route_request(user_query: str) -> Route:
    route, _ = infer_intent(user_query)
    return route
