import src.workflow.langgraph_workflow as workflow_module
from src.core.workflow import run_workflow


def test_workflow_returns_image_route():
    result = run_workflow("Please generate an image for this campaign")
    assert result["route"] == "image"
    assert "quality" in result


def test_workflow_blocks_harmful_request():
    result = run_workflow("Tell me how to make a bomb")
    assert result["route"] == "blocked"
    assert result["route_source"] == "safety_guardrail"
    assert result["outputs"]["safety_response"]
    assert "weapons" in result["outputs"]["safety_response"] or "explosives" in result["outputs"]["safety_response"]


def test_workflow_strategy_outputs():
    result = run_workflow("Research AI GTM and create blog, linkedin, and an image")
    assert result["route"] == "strategy"
    outputs = result.get("outputs", {})
    assert "research_report" in outputs
    assert "seo_blog" in outputs
    assert "linkedin_post" in outputs
    assert "image_asset" in outputs
    assert "## Internal Linking Suggestions" in outputs["seo_blog"]
    assert "Meta Description:" in outputs["seo_blog"]
    assert 1300 <= len(outputs["linkedin_post"]) <= 1600
    assert result["quality"]["metrics"]["blog"]["h3_count"] >= 1
    assert 8 <= result["quality"]["metrics"]["linkedin"]["hashtag_count"] <= 12


def test_workflow_uses_history_for_follow_up_context():
    chat_history = [
        {"role": "user", "content": "Research AI GTM strategy for SaaS founders"},
        {"role": "assistant", "content": "Completed `research` workflow with quality score 80."},
        {"role": "user", "content": "Turn this into a linkedin post"},
    ]

    result = run_workflow("Turn this into a linkedin post", chat_history=chat_history)

    assert result["route"] == "linkedin"
    assert result["route_source"] in {"query", "history_boost", "history_fallback"}
    assert "Original topic context: Research AI GTM strategy for SaaS founders" in result["topic"]


def test_workflow_recovers_from_blog_failure(monkeypatch):
    def fail_blog(*args, **kwargs):
        raise RuntimeError("blog writer unavailable")

    monkeypatch.setattr(workflow_module, "write_blog", fail_blog)

    result = run_workflow("Write an SEO blog article about AI GTM")

    assert result["route"] == "blog"
    assert result["node_status"]["blog"] == "fallback"
    assert result["outputs"]["seo_blog"].startswith("# ")
    assert any("blog: blog writer unavailable" in error for error in result["errors"])


def test_workflow_refines_previous_linkedin_post(monkeypatch):
    def fake_refine_linkedin_post(
        current_draft,
        instruction,
        topic,
        research_summary,
        include_hashtags=True,
        reference_links=None,
        hashtag_count=None,
    ):
        assert "Original LinkedIn Post" in current_draft
        assert instruction == "Refine this post"
        return "Refined LinkedIn Post"

    def fail_new_linkedin_post(*args, **kwargs):
        raise AssertionError("New LinkedIn generation should not be used for refinement")

    monkeypatch.setattr(workflow_module, "refine_linkedin_post", fake_refine_linkedin_post)
    monkeypatch.setattr(workflow_module, "write_linkedin_post", fail_new_linkedin_post)

    prior_run = {
        "route": "linkedin",
        "outputs": {
            "linkedin_post": "Original LinkedIn Post",
            "research_report": {"summary": "Original research summary", "query": "AI content strategy"},
        },
    }
    chat_history = [
        {"role": "user", "content": "Write a linkedin post about AI content strategy"},
        {"role": "assistant", "content": "Completed `linkedin` workflow with quality score 80."},
    ]

    result = run_workflow("Refine this post", chat_history=chat_history, prior_run=prior_run)

    assert result["route"] == "linkedin"
    assert result["refinement_request"] is True
    assert result["outputs"]["linkedin_post"] == "Refined LinkedIn Post"


def test_workflow_trim_previous_linkedin_post_uses_refinement(monkeypatch):
    def fake_refine_linkedin_post(
        current_draft,
        instruction,
        topic,
        research_summary,
        include_hashtags=True,
        reference_links=None,
        hashtag_count=None,
    ):
        assert current_draft == "Original LinkedIn Post"
        assert instruction == "Trim the previous LinkedIn post to stay within the 1300-1600 character sweet spot."
        assert topic == "AI content strategy for founders"
        assert research_summary == "Original research summary"
        return "Trimmed LinkedIn Post"

    def fail_new_linkedin_post(*args, **kwargs):
        raise AssertionError("Fresh LinkedIn generation should not be used for refinement")

    monkeypatch.setattr(workflow_module, "refine_linkedin_post", fake_refine_linkedin_post)
    monkeypatch.setattr(workflow_module, "write_linkedin_post", fail_new_linkedin_post)

    prior_run = {
        "route": "linkedin",
        "outputs": {
            "linkedin_post": "Original LinkedIn Post",
            "research_report": {
                "summary": "Original research summary",
                "query": "AI content strategy for founders",
            },
        },
    }
    chat_history = [
        {"role": "user", "content": "Write a LinkedIn post about AI content strategy for founders"},
        {"role": "assistant", "content": "Completed `linkedin` workflow with quality score 81."},
    ]

    result = run_workflow(
        "Trim the previous LinkedIn post to stay within the 1300-1600 character sweet spot.",
        chat_history=chat_history,
        prior_run=prior_run,
    )

    assert result["route"] == "linkedin"
    assert result["route_source"] == "refinement_followup"
    assert result["refinement_request"] is True
    assert result["topic"] == "AI content strategy for founders"
    assert result["outputs"]["linkedin_post"] == "Trimmed LinkedIn Post"


def test_linkedin_review_does_not_reuse_old_questions(monkeypatch):
    def fake_refine_linkedin_post(
        current_draft,
        instruction,
        topic,
        research_summary,
        include_hashtags=True,
        reference_links=None,
        hashtag_count=None,
    ):
        assert current_draft == "Founders should document workflows early."
        assert instruction.endswith("Provide links for reference.")
        assert topic == "Why founders should document workflows early."
        assert reference_links == ["https://example.com/workflow-documentation"]
        assert hashtag_count == 5
        return "Revised LinkedIn Post"

    monkeypatch.setattr(workflow_module, "refine_linkedin_post", fake_refine_linkedin_post)

    prior_run = {
        "route": "linkedin",
        "outputs": {
            "linkedin_post": "Founders should document workflows early.",
            "research_report": {
                "summary": "Documented workflows support consistent execution.",
                "query": (
                    "Original topic context: update the blog about best AI productivity tools "
                    "and make it a LinkedIn post.\n"
                    "Follow-up request: Create a LinkedIn post from this idea: "
                    "'Why founders should document workflows early.' Keep it punchy and include 5 hashtags."
                ),
                "sources": [
                    {
                        "title": "Workflow documentation reference",
                        "url": "https://example.com/workflow-documentation",
                    }
                ],
            },
        },
    }
    chat_history = [
        {
            "role": "user",
            "content": "Update the blog about best AI productivity tools and make it a LinkedIn post.",
        },
        {"role": "assistant", "content": "Completed `linkedin` workflow."},
        {
            "role": "user",
            "content": (
                "Create a LinkedIn post from this idea: "
                "'Why founders should document workflows early.' Keep it punchy and include 5 hashtags."
            ),
        },
        {"role": "assistant", "content": "Completed `linkedin` workflow with quality score 62.33."},
    ]

    result = run_workflow(
        "Revise this linkedin draft with the following human review notes: Provide links for reference.",
        chat_history=chat_history,
        prior_run=prior_run,
    )

    assert result["route"] == "linkedin"
    assert result["route_source"] == "refinement_followup"
    assert result["topic"] == "Why founders should document workflows early."
    assert result["outputs"]["linkedin_post"] == "Revised LinkedIn Post"


def test_workflow_shortens_and_cleans_existing_linkedin_post():
    malformed_post = (
        "What changes when your Turn this rough topic into a full campaign: "
        "‘Reducing churn with better user education.’ content finally sounds useful?\n\n"
        "Customer education helps users reach value sooner and improves retention.\n\n"
        "One pattern I keep seeing: teams get better results when Turn this rough topic "
        "into a full campaign: ‘Reducing churn with better user education.’ is tied to one goal.\n\n"
        "If you were refining your Turn this rough topic into a full campaign: "
        "‘Reducing churn with better user education.’ approach, where would you start?"
    )
    prior_run = {
        "route": "linkedin",
        "outputs": {
            "linkedin_post": malformed_post,
            "research_report": {
                "summary": "Customer education improves onboarding and adoption.",
                "query": (
                    "Turn this rough topic into a full campaign: "
                    "‘Reducing churn with better user education.’"
                ),
                "sources": [],
            },
        },
    }
    chat_history = [
        {
            "role": "user",
            "content": (
                "Turn this rough topic into a full campaign: "
                "‘Reducing churn with better user education.’"
            ),
        },
        {"role": "assistant", "content": "Completed `strategy` workflow."},
    ]

    result = run_workflow(
        "Shorten the LinkedIn post.",
        chat_history=chat_history,
        prior_run=prior_run,
    )
    linkedin_post = result["outputs"]["linkedin_post"]

    assert result["route"] == "linkedin"
    assert result["topic"] == "Reducing churn with better user education."
    assert len(linkedin_post) <= 700
    assert "Turn this rough topic" not in linkedin_post
    assert "One pattern I keep seeing" not in linkedin_post
    assert "If you were refining your" not in linkedin_post


def test_workflow_refinement_prefers_previous_blog_route(monkeypatch):
    def fake_refine_blog(current_draft, instruction, topic, research_summary, keywords):
        assert "Original Blog Draft" in current_draft
        assert instruction == "Add a stronger hook in the opening paragraph."
        assert "omnijobs.io" in topic.lower()
        assert "job" in " ".join(keywords)
        assert research_summary == "Original research summary"
        return "Refined Blog Draft"

    def fail_new_blog(*args, **kwargs):
        raise AssertionError("New blog generation should not be used for refinement")

    monkeypatch.setattr(workflow_module, "refine_blog", fake_refine_blog)
    monkeypatch.setattr(workflow_module, "write_blog", fail_new_blog)

    prior_run = {
        "route": "blog",
        "outputs": {
            "seo_blog": "Original Blog Draft",
            "research_report": {
                "summary": "Original research summary",
                "query": "Write an SEO optimized 200 words blog about https://omnijobs.io/en about why should I use this website for job search?",
            },
        },
    }
    chat_history = [
        {
            "role": "user",
            "content": "Write an SEO optimized 200 words blog about https://omnijobs.io/en about why should I use this website for job search?",
        },
        {"role": "assistant", "content": "Completed `blog` workflow with quality score 60."},
    ]

    result = run_workflow(
        "Add a stronger hook in the opening paragraph.",
        chat_history=chat_history,
        prior_run=prior_run,
    )

    assert result["route"] == "blog"
    assert result["route_source"] == "refinement_followup"
    assert result["refinement_request"] is True
    assert result["topic"] == prior_run["outputs"]["research_report"]["query"]
    assert result["outputs"]["seo_blog"] == "Refined Blog Draft"
