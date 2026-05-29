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


def evaluate_outputs(outputs: dict) -> dict:
    blog = outputs.get("seo_blog") or ""
    linkedin = outputs.get("linkedin_post") or ""
    research = (outputs.get("research_report") or {}).get("summary", "")

    scores = {
        "blog": quality_score(blog),
        "linkedin": quality_score(linkedin),
        "research": quality_score(research),
    }
    scores["overall"] = round(sum(scores.values()) / 3.0, 2)

    improvements = []
    if scores["blog"] < 75:
        improvements.append("Expand blog structure with more headings and examples.")
    if scores["linkedin"] < 70:
        improvements.append("Strengthen hook and ending question in LinkedIn copy.")
    if scores["research"] < 70:
        improvements.append("Add more concrete data points or citations in research summary.")

    return {"scores": scores, "improvements": improvements}
