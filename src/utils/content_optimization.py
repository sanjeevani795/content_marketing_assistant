import math
import re
from typing import Optional


def extract_keywords(user_query: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]+", user_query.lower())
    stop = {
        "about",
        "with",
        "that",
        "this",
        "from",
        "into",
        "for",
        "and",
        "the",
        "create",
        "write",
        "generate",
        "blog",
        "blogs",
        "post",
        "posts",
        "article",
        "articles",
        "word",
        "words",
        "guide",
        "draft",
        "website",
        "site",
        "optimized",
        "linkedin",
        "http",
        "https",
        "www",
        "com",
        "en",
        "io",
    }
    filtered = [t for t in tokens if len(t) > 3 and t not in stop]
    seen = set()
    dedup = []
    for token in filtered:
        if token not in seen:
            dedup.append(token)
            seen.add(token)
    return dedup[:10]


def _normalize_lines(content: str) -> list[str]:
    return [line.rstrip() for line in content.strip().splitlines()]


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"\b[a-z0-9-]+\b", text.lower())


def _keyword_occurrences(text: str, keyword: str) -> int:
    if not keyword.strip():
        return 0
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return len(re.findall(pattern, text.lower()))


def keyword_density(text: str, keyword: str) -> float:
    words = _word_tokens(text)
    if not words or not keyword.strip():
        return 0.0
    occurrences = _keyword_occurrences(text, keyword)
    return round((occurrences / len(words)) * 100.0, 2)


def _desired_keyword_bounds(word_count: int) -> tuple[int, int]:
    if word_count <= 0:
        return 1, 1
    minimum = max(1, math.ceil(word_count * 0.01))
    maximum = max(minimum, math.floor(word_count * 0.02))
    return minimum, maximum


def _count_syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 1
    vowels = "aeiouy"
    syllables = 0
    prev_vowel = False
    for char in cleaned:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            syllables += 1
        prev_vowel = is_vowel
    if cleaned.endswith("e") and syllables > 1:
        syllables -= 1
    return max(1, syllables)


def _build_dilution_paragraph(words_needed: int) -> str:
    neutral_sentences = [
        "Add one more example, one customer proof point, and one distribution note to keep the article balanced and readable.",
        "Include a practical implementation detail so the guidance feels specific, useful, and easier to apply in a real workflow.",
        "A short note on measurement, iteration, and execution can make the article more complete without repeating the same phrase.",
    ]
    parts = []
    while len(_word_tokens(" ".join(parts))) < words_needed:
        parts.append(neutral_sentences[len(parts) % len(neutral_sentences)])
        if len(parts) >= len(neutral_sentences):
            break
    return " ".join(parts)


def readability_score(text: str) -> float:
    words = _word_tokens(text)
    if not words:
        return 0.0

    sentences = re.split(r"[.!?]+", text)
    sentence_count = max(1, len([s for s in sentences if s.strip()]))
    word_count = len(words)
    syllable_count = sum(_count_syllables(word) for word in words)

    grade = 0.39 * (word_count / sentence_count) + 11.8 * (
        syllable_count / word_count
    ) - 15.59
    return round(max(0.0, grade), 2)


def _extract_title(content: str, primary_keyword: str) -> str:
    for line in _normalize_lines(content):
        if line.startswith("# "):
            return line[2:].strip()
    return primary_keyword.strip().title()


def _ensure_h1(content: str, primary_keyword: str) -> str:
    lines = _normalize_lines(content)
    if not lines:
        return f"# {primary_keyword.title()}"
    rebuilt = []
    h1_seen = False
    for line in lines:
        if line.startswith("# "):
            if not h1_seen:
                rebuilt.append(line)
                h1_seen = True
            else:
                rebuilt.append("## " + line[2:].strip())
        else:
            rebuilt.append(line)
    if h1_seen:
        return "\n".join(rebuilt)
    return "\n".join([f"# {primary_keyword.title()}", "", *rebuilt]).strip()


def _ensure_h2_h3(content: str, primary_keyword: str) -> str:
    lines = _normalize_lines(content)
    h2_count = sum(1 for line in lines if line.startswith("## "))
    h3_count = sum(1 for line in lines if line.startswith("### "))

    if h2_count == 0:
        lines.extend(
            [
                "",
                "## Why It Matters",
                f"{primary_keyword.title()} helps teams align search intent with measurable business outcomes.",
                "",
                "## Practical Next Steps",
                "Use this framework to turn the topic into a repeatable content workflow.",
            ]
        )
    elif h2_count == 1:
        lines.extend(
            [
                "",
                "## Practical Next Steps",
                "Turn the insights above into a publishable brief, supporting assets, and clear CTAs.",
            ]
        )

    if h3_count == 0:
        insertion_index = len(lines)
        for idx, line in enumerate(lines):
            if line.startswith("## Conclusion"):
                insertion_index = idx
                break
        h3_block = [
            "",
            "### Execution Tips",
            "Prioritize examples, proof points, and one clear CTA to keep the narrative focused.",
        ]
        lines[insertion_index:insertion_index] = h3_block

    return "\n".join(lines).strip()


def _ensure_keyword_density(content: str, primary_keyword: str) -> str:
    words = _word_tokens(content)
    minimum, maximum = _desired_keyword_bounds(len(words))
    current = _keyword_occurrences(content, primary_keyword)
    density_fillers = [
        f"{primary_keyword.title()} gives teams a clearer path from planning to execution.",
        f"Strong {primary_keyword} decisions work best when they connect audience needs to measurable outcomes.",
        f"Use {primary_keyword} as the thread that keeps strategy, distribution, and conversion aligned.",
    ]
    insertion_count = 0

    while current < minimum and insertion_count < len(density_fillers):
        content += f"\n\n{density_fillers[insertion_count]}"
        words = _word_tokens(content)
        minimum, maximum = _desired_keyword_bounds(len(words))
        current = _keyword_occurrences(content, primary_keyword)
        insertion_count += 1

    dilution_count = 0
    while words and current > maximum and dilution_count < 2:
        required_total_words = max(len(words), math.ceil(current / 0.02))
        extra_words_needed = max(20, required_total_words - len(words))
        content += f"\n\n{_build_dilution_paragraph(extra_words_needed)}"
        words = _word_tokens(content)
        minimum, maximum = _desired_keyword_bounds(len(words))
        current = _keyword_occurrences(content, primary_keyword)
        dilution_count += 1

    return content


def _fit_to_length(text: str, minimum: int, maximum: int) -> str:
    trimmed = " ".join(text.split())
    if len(trimmed) > maximum:
        cutoff = trimmed[: maximum + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
        trimmed = cutoff
    padding_options = [
        " Fast.",
        " Today.",
        " Clearly.",
        " With examples.",
        " For better results.",
        " Built for modern teams.",
    ]
    index = 0
    while len(trimmed) < minimum:
        addition = padding_options[index % len(padding_options)]
        if len(trimmed) + len(addition) <= maximum:
            trimmed += addition
        else:
            break
        index += 1
    return trimmed


def generate_meta_description(content: str, primary_keyword: str) -> str:
    title = _extract_title(content, primary_keyword)
    title_fragment = (
        "a practical framework"
        if title.lower() == primary_keyword.lower()
        else title.lower()
    )
    base = (
        f"Learn {primary_keyword} through {title_fragment}, practical examples, stronger headers, "
        "internal linking ideas, and actionable steps your team can publish and repurpose fast."
    )
    return _fit_to_length(base, 150, 160)


def internal_link_suggestions(
    primary_keyword: str, secondary_keywords: Optional[list[str]] = None
) -> list[str]:
    supporting = [keyword for keyword in (secondary_keywords or []) if keyword != primary_keyword]
    suggestions = [
        f"Link to a pillar page about {primary_keyword}.",
        "Add a supporting link to a case study showing measurable results on this topic.",
        "Connect to a CTA page, template, or workflow checklist for conversion.",
    ]
    for keyword in supporting[:2]:
        suggestions.append(f"Reference a related article on {keyword}.")
    return suggestions[:4]


def _append_internal_links(
    content: str, primary_keyword: str, secondary_keywords: Optional[list[str]] = None
) -> str:
    if "## Internal Linking Suggestions" in content:
        return content
    bullets = "\n".join(
        f"- {item}" for item in internal_link_suggestions(primary_keyword, secondary_keywords)
    )
    return content.rstrip() + "\n\n## Internal Linking Suggestions\n" + bullets


def optimize_for_seo(
    content: str, primary_keyword: str, secondary_keywords: Optional[list[str]] = None
) -> str:
    optimized = _ensure_h1(content, primary_keyword)
    optimized = _ensure_h2_h3(optimized, primary_keyword)
    optimized = _append_internal_links(optimized, primary_keyword, secondary_keywords)

    meta_line = "Meta Description:"
    meta_description = generate_meta_description(optimized, primary_keyword)
    if meta_line.lower() in optimized.lower():
        optimized = re.sub(
            r"Meta Description:.*",
            f"Meta Description: {meta_description}",
            optimized,
            flags=re.IGNORECASE,
        )
    else:
        optimized = optimized.rstrip() + f"\n\nMeta Description: {meta_description}"

    optimized = _ensure_keyword_density(optimized, primary_keyword)
    return optimized.strip()


def _split_hashtag_block(text: str) -> tuple[str, list[str]]:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    hashtags: list[str] = []
    while lines and lines[-1].strip().startswith("#"):
        hashtags = re.findall(r"#\w+", lines.pop()) + hashtags
    body = "\n".join(lines).strip()
    return body, hashtags


def _unique_hashtags(topic: str) -> list[str]:
    topic_tokens = [token for token in extract_keywords(topic) if token.isalnum()][:5]
    tags = [
        "#ContentMarketing",
        "#SEO",
        "#LinkedInStrategy",
        "#DemandGen",
        "#B2BMarketing",
        "#ThoughtLeadership",
        "#ContentStrategy",
        "#DigitalMarketing",
        "#AI",
        "#MarketingOps",
    ]
    for token in topic_tokens:
        tags.insert(0, "#" + token.title().replace("-", ""))

    deduped = []
    seen = set()
    for tag in tags:
        normalized = tag.lower()
        if normalized not in seen:
            deduped.append(tag)
            seen.add(normalized)
    return deduped[:10]


def _ensure_hook(body: str, topic: str) -> str:
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    if not paragraphs:
        return f"Most teams do not need more content. They need a sharper {topic} strategy."
    first = paragraphs[0]
    if "?" in first:
        return body
    hook = f"What changes when your {topic} content finally sounds like it belongs to one strategy?"
    return hook + "\n\n" + body


def _ensure_cta(body: str, topic: str) -> str:
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    if paragraphs and paragraphs[-1].endswith("?"):
        return body
    return body.rstrip() + (
        f"\n\nIf you were refining your {topic} approach this quarter, where would you start first?"
    )


def _expand_or_trim_body(body: str, topic: str, research_summary: str) -> str:
    expanded = body.strip()
    filler_blocks = [
        (
            f"One pattern I keep seeing: teams get better results when {topic} is tied to one audience pain point, "
            "one business goal, and one clear distribution plan."
        ),
        (
            "A simple way to improve this: build one strong source asset, pull out the most useful proof point, "
            "and adapt it into channel-specific formats instead of rewriting from scratch."
        ),
        (
            f"Here is the practical takeaway: {research_summary[:260].strip() or 'research-backed specifics outperform generic commentary when buyers need confidence.'}"
        ),
    ]

    for block in filler_blocks:
        if len(expanded) >= 1300:
            break
        if block.lower() not in expanded.lower():
            expanded += "\n\n" + block

    if len(expanded) > 1450:
        shortened = expanded[:1450]
        expanded = shortened.rsplit(" ", 1)[0].rstrip(" ,;:-") + "."

    return expanded


def _optimize_line_breaks(body: str) -> str:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", body) if part.strip()]
    paragraphs = []
    current = []
    for sentence in sentences:
        current.append(sentence)
        if len(current) == 2 or len(" ".join(current)) > 240:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


def optimize_linkedin_post(
    content: str, topic: str, research_summary: str, include_hashtags: bool = True
) -> str:
    body, _ = _split_hashtag_block(content)
    body = _ensure_hook(body, topic)
    body = _expand_or_trim_body(body, topic, research_summary)
    body = _optimize_line_breaks(body)

    if len(body) > 1510:
        body = body[:1510].rsplit(" ", 1)[0].rstrip(" ,;:-") + "?"

    hashtags = _unique_hashtags(topic) if include_hashtags else []
    if include_hashtags:
        hashtag_line = " ".join(hashtags)
        while len(body) + 4 + len(hashtag_line) < 1300:
            body += "\n\nThe teams that win here usually communicate with more clarity, more proof, and more personality."
        body = _ensure_cta(body, topic)
        if len(body) + 4 + len(hashtag_line) > 1600:
            allowed = 1600 - len(hashtag_line) - 4
            body = body[:allowed].rsplit(" ", 1)[0].rstrip(" ,;:-") + "."
            body = _ensure_cta(body, topic)
        return body.strip() + "\n\n" + hashtag_line

    if len(body) < 1300:
        body = _expand_or_trim_body(body, topic, research_summary)
    body = _ensure_cta(body, topic)
    if len(body) > 1600:
        body = body[:1600].rsplit(" ", 1)[0].rstrip(" ,;:-") + "."
        body = _ensure_cta(body, topic)
    return body.strip()


def analyze_seo_content(content: str, primary_keyword: str) -> dict:
    headers = _normalize_lines(content)
    meta_match = re.search(r"Meta Description:\s*(.+)", content, flags=re.IGNORECASE)
    meta_description = meta_match.group(1).strip() if meta_match else ""
    return {
        "keyword_density": keyword_density(content, primary_keyword),
        "readability_grade": readability_score(content),
        "meta_description_length": len(meta_description),
        "h1_count": sum(1 for line in headers if line.startswith("# ")),
        "h2_count": sum(1 for line in headers if line.startswith("## ")),
        "h3_count": sum(1 for line in headers if line.startswith("### ")),
        "internal_link_suggestions": content.count("## Internal Linking Suggestions"),
    }


def analyze_linkedin_post(content: str) -> dict:
    body, hashtags = _split_hashtag_block(content)
    paragraphs = [part for part in body.split("\n\n") if part.strip()]
    return {
        "character_count": len(content),
        "hashtag_count": len(hashtags),
        "has_hooks": "?" in paragraphs[0] if paragraphs else False,
        "has_cta": body.rstrip().endswith("?"),
        "paragraph_count": len(paragraphs),
    }
