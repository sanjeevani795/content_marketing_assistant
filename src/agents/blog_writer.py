from src.integrations.openai_client import OpenAIClient
from src.utils.content_optimization import optimize_for_seo


def _fallback_blog(topic: str, keywords: list[str], research_summary: str) -> str:
    primary = keywords[0] if keywords else topic
    return f"""# {topic}

## Introduction
{research_summary[:350]}

## Why This Matters
Organizations that align content strategy to measurable user intent outperform one-off publishing.

## Practical Framework
1. Define audience pain points tied to business outcomes.
2. Build one flagship asset with data and examples.
3. Repurpose into channel-specific formats.

## Implementation Checklist
- Map keyword clusters to funnel stages.
- Publish with clear CTA and internal links.
- Measure CTR, engagement time, and conversion influence.

## Conclusion
Use this framework to turn research into repeatable content operations.

**Primary keyword:** {primary}
"""


def write_blog(topic: str, research_summary: str, keywords: list[str]) -> str:
    llm = OpenAIClient()
    primary = keywords[0] if keywords else topic

    if llm.enabled:
        draft = llm.generate(
            prompt=(
                f"Write an SEO-optimized blog post on: {topic}.\n"
                f"Primary keyword: {primary}.\n"
                f"Secondary keywords: {', '.join(keywords[1:6]) if len(keywords) > 1 else 'N/A'}.\n"
                f"Use this research context:\n{research_summary}\n"
                "Include: compelling title, H2/H3 headings, practical examples, and conclusion with CTA."
            ),
            system="You are an expert SEO blog writer.",
            temperature=0.5,
        )
    else:
        draft = _fallback_blog(topic, keywords, research_summary)

    return optimize_for_seo(draft, primary_keyword=primary)
