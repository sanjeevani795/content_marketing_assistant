from src.integrations.openai_client import OpenAIClient
from src.core.observability import traceable
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

### Execution Tips
- Use the target keyword naturally in headings and conclusion copy.
- Keep examples specific enough to support internal links and conversion paths.

## Implementation Checklist
- Map keyword clusters to funnel stages.
- Publish with clear CTA and internal links.
- Measure CTR, engagement time, and conversion influence.

## Conclusion
Use this framework to turn research into repeatable content operations.

**Primary keyword:** {primary}
"""


@traceable(name="seo_blog_writer_agent", run_type="chain")
def write_blog(topic: str, research_summary: str, keywords: list[str]) -> str:
    llm = OpenAIClient()
    primary = keywords[0] if keywords else topic
    secondary = keywords[1:6]

    if llm.enabled:
        draft = llm.generate(
            prompt=(
                f"Write an SEO-optimized blog post on: {topic}.\n"
                f"Primary keyword: {primary}.\n"
                f"Secondary keywords: {', '.join(secondary) if secondary else 'N/A'}.\n"
                f"Use this research context:\n{research_summary}\n"
                "Include: compelling title, H2/H3 headings, practical examples, internal link ideas, "
                "a conclusion with CTA, and natural target keyword usage."
            ),
            system="You are an expert SEO blog writer.",
            temperature=0.5,
        )
    else:
        draft = _fallback_blog(topic, keywords, research_summary)

    return optimize_for_seo(
        draft,
        primary_keyword=primary,
        secondary_keywords=secondary,
    )


@traceable(name="seo_blog_refinement_agent", run_type="chain")
def refine_blog(
    current_draft: str,
    instruction: str,
    topic: str,
    research_summary: str,
    keywords: list[str],
) -> str:
    llm = OpenAIClient()
    primary = keywords[0] if keywords else topic
    secondary = keywords[1:6]

    if llm.enabled:
        refined = llm.generate(
            prompt=(
                f"Refine this existing SEO blog draft based on the user instruction.\n"
                f"User instruction: {instruction}\n"
                f"Topic: {topic}\n"
                f"Primary keyword: {primary}\n"
                f"Secondary keywords: {', '.join(secondary) if secondary else 'N/A'}\n"
                f"Research context:\n{research_summary}\n\n"
                f"Current draft:\n{current_draft}\n\n"
                "Keep the strongest ideas, revise the actual draft instead of starting over, and preserve markdown structure."
            ),
            system="You are an expert SEO editor refining an existing blog draft.",
            temperature=0.4,
        )
    else:
        refined = (
            current_draft.rstrip()
            + f"\n\n## Refinement Notes\nThis version was refined to address the follow-up request: {instruction}."
        )

    return optimize_for_seo(
        refined,
        primary_keyword=primary,
        secondary_keywords=secondary,
    )
