from src.core.router import infer_intent, route_request


def test_blog_route():
    assert route_request("Write an SEO blog article") == "blog"


def test_linkedin_route():
    assert route_request("Create a linkedin post with hashtags") == "linkedin"


def test_strategy_when_multi_format_requested():
    route, scores = infer_intent("Do deep research and write blog plus LinkedIn post with image")
    assert route == "strategy"
    assert scores["strategy"] >= 2
