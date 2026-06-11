from src.utils.quality_validation import evaluate_outputs


def test_quality_validation_flags_blog_and_linkedin_review_thresholds():
    outputs = {
        "seo_blog": "",
        "linkedin_post": "",
        "research_report": {"summary": "A short research summary.", "query": "AI content strategy"},
    }

    result = evaluate_outputs(outputs)

    assert result["thresholds"]["blog"] == 50.0
    assert result["thresholds"]["linkedin"] == 60.0
    assert result["review_required"]["blog"] is True
    assert result["review_required"]["linkedin"] is True


def test_quality_validation_scores_only_outputs_present_in_run():
    outputs = {
        "research_report": {
            "summary": "A detailed research summary. " * 60,
            "query": "Compare AI in B2B sales content angles",
        },
    }

    result = evaluate_outputs(outputs)

    assert result["scores"]["overall"] == result["scores"]["research"]
    assert "blog" not in result["scores"]
    assert "linkedin" not in result["scores"]
    assert "blog" not in result["review_required"]
    assert "linkedin" not in result["review_required"]
    assert "blog" not in result["metrics"]
    assert "linkedin" not in result["metrics"]
    assert all("blog" not in item.lower() for item in result["improvements"])
    assert all("linkedin" not in item.lower() for item in result["improvements"])


def test_quality_validation_does_not_flag_high_linkedin_score_for_review():
    outputs = {
        "seo_blog": "# Strong Blog\n\n## Section\n\n### Detail\n\nMeta Description: Actionable guide to AI content strategy for growth teams with examples, structure, and steps for stronger execution today.",
        "linkedin_post": (
            "What changes when your AI content strategy finally sounds like one system?\n\n"
            "Teams often create too much content and too little clarity. The win usually comes from one sharp message, "
            "one proof point, and one clear next step.\n\n"
            "Build one strong source asset, turn it into channel-native variations, and keep the tone consistent across each touchpoint.\n\n"
            "That shift creates stronger trust, better engagement, and more useful conversations with the right audience.\n\n"
            "If you were refining your content strategy this quarter, what would you change first?\n\n"
            "#AI #ContentStrategy #ContentMarketing #SEO #DemandGen #B2BMarketing #ThoughtLeadership #MarketingOps"
        ),
        "research_report": {"summary": "Practical, readable research summary with a few useful specifics.", "query": "AI content strategy"},
    }

    result = evaluate_outputs(outputs)

    assert result["scores"]["linkedin"] >= 60.0
    assert result["review_required"]["linkedin"] is False
