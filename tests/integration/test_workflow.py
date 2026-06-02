import src.workflow.langgraph_workflow as workflow_module
from src.core.workflow import run_workflow


def test_workflow_returns_image_route():
    result = run_workflow("Please generate an image for this campaign")
    assert result["route"] == "image"
    assert "quality" in result


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
    def fake_refine_linkedin_post(current_draft, instruction, topic, research_summary, include_hashtags=True):
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
