from src.utils.content_optimization import (
    analyze_linkedin_post,
    analyze_seo_content,
    extract_keywords,
    readability_score,
)

BLOG_REVIEW_THRESHOLD = 50.0
LINKEDIN_REVIEW_THRESHOLD = 60.0
RESEARCH_REVIEW_THRESHOLD = 70.0


def quality_score(content: str) -> float:
    text = (content or "").strip()
    if not text:
        return 0.0

    score = 55.0
    length = len(text)
    if length > 900:
        score += 20
    elif length > 450:
        score += 12
    else:
        score += 5

    if "##" in text:
        score += 8
    if "Meta Description:" in text:
        score += 7
    if "?" in text:
        score += 3

    return min(100.0, score)


def _blog_score(blog: str, research_report: dict) -> tuple[float, dict, list[str]]:
    query = (research_report or {}).get("query", "")
    candidate_keywords = extract_keywords(query or blog)
    keyword = candidate_keywords[0] if candidate_keywords else "content strategy"
    metrics = analyze_seo_content(blog, keyword)
    score = quality_score(blog)
    improvements = []

    if 1.0 <= metrics["keyword_density"] <= 2.0:
        score += 8
    elif metrics["keyword_density"] < 1.0:
        improvements.append("Increase target keyword usage toward the 1-2% range.")
    else:
        improvements.append("Reduce target keyword repetition to stay near the 1-2% range.")

    if 150 <= metrics["meta_description_length"] <= 160:
        score += 7
    else:
        improvements.append("Adjust the meta description to 150-160 characters.")

    if metrics["h1_count"] == 1 and metrics["h2_count"] >= 2 and metrics["h3_count"] >= 1:
        score += 8
    else:
        improvements.append("Strengthen blog header structure with one H1, multiple H2s, and at least one H3.")

    if metrics["internal_link_suggestions"] >= 1:
        score += 5
    else:
        improvements.append("Add internal linking suggestions to guide related content journeys.")

    if metrics["readability_grade"] <= 12:
        score += 7
    else:
        improvements.append("Lower the Flesch-Kincaid grade for easier scanning.")

    return min(100.0, round(score, 2)), metrics, improvements


def _linkedin_score(linkedin: str) -> tuple[float, dict, list[str]]:
    metrics = analyze_linkedin_post(linkedin)
    score = quality_score(linkedin)
    improvements = []

    if 1300 <= metrics["character_count"] <= 1600:
        score += 10
    elif metrics["character_count"] < 1300:
        improvements.append("Expand the LinkedIn post to the 1300-1600 character sweet spot.")
    else:
        improvements.append("Trim the LinkedIn post to stay within the 1300-1600 character sweet spot.")

    if 8 <= metrics["hashtag_count"] <= 12:
        score += 8
    else:
        improvements.append("Use 8-12 relevant hashtags for discoverability without clutter.")

    if metrics["has_hooks"]:
        score += 6
    else:
        improvements.append("Add a stronger hook in the opening paragraph.")

    if metrics["has_cta"]:
        score += 6
    else:
        improvements.append("End with a clearer engagement prompt or CTA question.")

    if metrics["paragraph_count"] >= 4:
        score += 5
    else:
        improvements.append("Increase line breaks so the post is easier to read on LinkedIn.")

    return min(100.0, round(score, 2)), metrics, improvements


def evaluate_outputs(outputs: dict, errors: list[str] = None) -> dict:
    errors = errors or []
    scores = {}
    review_required = {}
    improvements = []
    metrics = {}

    research_report = outputs.get("research_report") or {}
    if "research_report" in outputs:
        research = research_report.get("summary", "")
        research_score = quality_score(research)
        research_readability = readability_score(research)
        if research_readability <= 12 and research:
            research_score = min(100.0, round(research_score + 5, 2))

        scores["research"] = research_score
        review_required["research"] = research_score < RESEARCH_REVIEW_THRESHOLD
        metrics["research"] = {
            "readability_grade": research_readability,
            "character_count": len(research),
        }
        if review_required["research"]:
            improvements.append("Add more concrete data points or citations in research summary.")

    if "seo_blog" in outputs:
        blog_score, blog_metrics, blog_improvements = _blog_score(
            outputs.get("seo_blog") or "", research_report
        )
        scores["blog"] = blog_score
        review_required["blog"] = blog_score < BLOG_REVIEW_THRESHOLD
        metrics["blog"] = blog_metrics
        improvements.extend(blog_improvements)

    if "linkedin_post" in outputs:
        linkedin_score, linkedin_metrics, linkedin_improvements = _linkedin_score(
            outputs.get("linkedin_post") or ""
        )
        scores["linkedin"] = linkedin_score
        review_required["linkedin"] = linkedin_score < LINKEDIN_REVIEW_THRESHOLD
        metrics["linkedin"] = linkedin_metrics
        improvements.extend(linkedin_improvements)

    applicable_scores = list(scores.values())
    scores["overall"] = (
        round(sum(applicable_scores) / len(applicable_scores), 2)
        if applicable_scores
        else 0.0
    )
    if errors:
        scores["overall"] = max(0.0, round(scores["overall"] - min(15.0, len(errors) * 5.0), 2))

    if errors:
        improvements.append("Review fallback outputs because one or more agents hit an execution error.")

    return {
        "scores": scores,
        "thresholds": {
            "blog": BLOG_REVIEW_THRESHOLD,
            "linkedin": LINKEDIN_REVIEW_THRESHOLD,
            "research": RESEARCH_REVIEW_THRESHOLD,
        },
        "review_required": review_required,
        "improvements": improvements,
        "errors": errors,
        "metrics": metrics,
    }
