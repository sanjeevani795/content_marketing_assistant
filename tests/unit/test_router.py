from src.core.router import build_topic, infer_intent, is_refinement_query, route_request


def test_blog_route():
    assert route_request("Write an SEO blog article") == "blog"


def test_linkedin_route():
    assert route_request("Create a linkedin post with hashtags") == "linkedin"


def test_strategy_when_multi_format_requested():
    route, scores, details = infer_intent(
        "Do deep research and write blog plus LinkedIn post with image"
    )
    assert route == "strategy"
    assert scores["strategy"] >= 2
    assert details["route_source"] == "query"


def test_ambiguous_route_falls_back_to_research():
    route, _, details = infer_intent("Can you help with this?")
    assert route == "research"
    assert details["ambiguous"] is True
    assert details["route_source"] == "ambiguity_fallback"


def test_history_guides_follow_up_route():
    chat_history = [
        {"role": "user", "content": "Write an SEO blog article about content operations"},
        {"role": "assistant", "content": "Completed `blog` workflow with quality score 82."},
    ]

    route, _, details = infer_intent("Make it shorter", chat_history=chat_history)

    assert route == "blog"
    assert details["history_used"] is True
    assert details["route_source"] == "history_fallback"


def test_build_topic_uses_previous_user_context_for_follow_up():
    topic = build_topic(
        "Turn this into a LinkedIn post",
        chat_history=[
            {"role": "user", "content": "Research AI GTM strategy for SaaS founders"},
            {"role": "assistant", "content": "Completed `research` workflow with quality score 80."},
        ],
    )

    assert "Original topic context: Research AI GTM strategy for SaaS founders" in topic


def test_build_topic_prefers_explicit_idea_over_old_history():
    topic = build_topic(
        "Create a LinkedIn post from this idea: 'Why founders should document workflows early.' Keep it punchy and include 5 hashtags.",
        chat_history=[
            {
                "role": "user",
                "content": "Update the blog about best AI productivity tools and make it a LinkedIn post.",
            },
            {"role": "assistant", "content": "Completed `linkedin` workflow."},
        ],
    )

    assert topic == "Why founders should document workflows early."
    assert "Original topic context" not in topic


def test_detects_refinement_query():
    assert is_refinement_query("Refine this post") is True
    assert is_refinement_query("Make it shorter") is True
    assert is_refinement_query("Add a stronger hook in the opening paragraph.") is True
    assert is_refinement_query("Trim the previous LinkedIn post to stay within the 1300-1600 character sweet spot.") is True
    assert is_refinement_query("Create a new campaign plan") is False
