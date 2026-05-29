import re


def extract_keywords(user_query: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]+", user_query.lower())
    stop = {"about", "with", "that", "this", "from", "into", "for", "and", "the", "create", "write", "generate"}
    filtered = [t for t in tokens if len(t) > 3 and t not in stop]
    # Preserve order, remove duplicates.
    seen = set()
    dedup = []
    for token in filtered:
        if token not in seen:
            dedup.append(token)
            seen.add(token)
    return dedup[:10]


def optimize_for_seo(content: str, primary_keyword: str) -> str:
    if primary_keyword.lower() not in content.lower():
        content = f"{content}\n\nKeyword focus: {primary_keyword}"
    if "meta description" not in content.lower():
        content += (
            "\n\nMeta Description: "
            f"Actionable guide on {primary_keyword} with frameworks, examples, and implementation steps."
        )
    return content
