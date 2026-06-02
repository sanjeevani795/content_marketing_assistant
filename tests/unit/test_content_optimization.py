import re

from src.utils.content_optimization import (
    analyze_linkedin_post,
    analyze_seo_content,
    keyword_density,
    optimize_for_seo,
    optimize_linkedin_post,
    readability_score,
)


def test_optimize_for_seo_enforces_required_blog_elements():
    draft = """Content operations can drift when teams publish without a system.

## Framework
Use audience pain points, proof, and repurposing discipline.

## Conclusion
Ship one strong asset and adapt it across channels.
"""

    optimized = optimize_for_seo(
        draft,
        primary_keyword="content operations",
        secondary_keywords=["seo workflow", "internal links"],
    )
    metrics = analyze_seo_content(optimized, "content operations")

    assert optimized.startswith("# ")
    assert "### Execution Tips" in optimized
    assert "## Internal Linking Suggestions" in optimized
    assert 150 <= metrics["meta_description_length"] <= 160
    assert metrics["h1_count"] == 1
    assert metrics["h2_count"] >= 2
    assert metrics["h3_count"] >= 1
    assert 1.0 <= metrics["keyword_density"] <= 2.0
    assert metrics["internal_link_suggestions"] == 1
    assert readability_score(optimized) > 0


def test_optimize_linkedin_post_enforces_length_and_hashtags():
    draft = (
        "Most teams are posting consistently but still not creating trust.\n\n"
        "The problem is usually message clarity, not effort.\n\n"
        "Build from one strong insight and adapt it with intention."
    )

    optimized = optimize_linkedin_post(
        draft,
        topic="AI content strategy",
        research_summary="Research shows practical examples and repeatable positioning improve engagement and conversion.",
        include_hashtags=True,
    )
    metrics = analyze_linkedin_post(optimized)
    hashtags = re.findall(r"#\w+", optimized)

    assert 1300 <= len(optimized) <= 1600
    assert 8 <= len(hashtags) <= 12
    assert metrics["has_hooks"] is True
    assert metrics["has_cta"] is True
    assert metrics["paragraph_count"] >= 4


def test_keyword_density_reports_percentage():
    content = "SEO strategy improves results. A clear SEO strategy creates better planning."
    assert keyword_density(content, "seo strategy") > 0
