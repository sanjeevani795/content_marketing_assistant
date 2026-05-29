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
