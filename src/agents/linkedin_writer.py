import re
from typing import Optional

from src.integrations.openai_client import OpenAIClient
from src.core.observability import traceable
from src.utils.content_optimization import optimize_linkedin_post


def _requested_hashtag_count(*instructions: str) -> Optional[int]:
    for instruction in instructions:
        match = re.search(r"\b(\d{1,2})\s+hashtags?\b", instruction, flags=re.IGNORECASE)
        if match:
            return min(20, max(1, int(match.group(1))))
    return None


def _reference_context(reference_links: Optional[list[str]]) -> str:
    links = [link for link in (reference_links or []) if link.startswith(("http://", "https://"))]
    if not links:
        return "No verified reference links are available. Do not invent URLs."
    return "Verified reference links:\n" + "\n".join(f"- {link}" for link in links)


def _append_requested_references(
    content: str, instruction: str, reference_links: Optional[list[str]]
) -> str:
    if not re.search(r"\b(?:links?|references?|sources?)\b", instruction, flags=re.IGNORECASE):
        return content

    links = [
        link
        for link in (reference_links or [])
        if link.startswith(("http://", "https://")) and link not in content
    ]
    if not links:
        return content
    return content.rstrip() + "\n\nReferences:\n" + "\n".join(links)


@traceable(name="linkedin_post_writer_agent", run_type="chain")
def write_linkedin_post(
    topic: str,
    research_summary: str,
    include_hashtags: bool = True,
    instruction: str = "",
    reference_links: Optional[list[str]] = None,
    hashtag_count: Optional[int] = None,
) -> str:
    llm = OpenAIClient()
    hashtag_count = hashtag_count or _requested_hashtag_count(instruction, topic)

    if llm.enabled:
        post = llm.generate(
            prompt=(
                f"Write a high-engagement LinkedIn post on: {topic}.\n"
                f"User request: {instruction or 'Create a LinkedIn post.'}\n"
                f"Context:\n{research_summary}\n"
                f"{_reference_context(reference_links)}\n"
                "Use: strong hook, short paragraphs, one tactical takeaway, a clear CTA question, "
                "professional tone with personality, and line breaks that feel easy to scan on mobile. "
                "Include verified reference links when the user asks for references. "
                "Return only the finished LinkedIn post; never repeat prompt labels or conversation history."
            ),
            system="You are a LinkedIn content strategist.",
            temperature=0.7,
        )
    else:
        post = (
            f"Most teams do not have a content problem. They have a positioning problem.\n\n"
            f"Topic: {topic}\n"
            f"Insight: {research_summary[:220]}\n\n"
            "Try this this week: build one research-led asset, then repurpose into channel-native formats.\n\n"
            "What would this change in your content workflow?"
        )
    post = _append_requested_references(post, instruction, reference_links)

    return optimize_linkedin_post(
        post,
        topic=topic,
        research_summary=research_summary,
        include_hashtags=include_hashtags,
        hashtag_count=hashtag_count,
    )


@traceable(name="linkedin_post_refinement_agent", run_type="chain")
def refine_linkedin_post(
    current_draft: str,
    instruction: str,
    topic: str,
    research_summary: str,
    include_hashtags: bool = True,
    reference_links: Optional[list[str]] = None,
    hashtag_count: Optional[int] = None,
) -> str:
    llm = OpenAIClient()
    hashtag_count = hashtag_count or _requested_hashtag_count(instruction, topic)

    if llm.enabled:
        refined = llm.generate(
            prompt=(
                f"Refine this existing LinkedIn post based on the user instruction.\n"
                f"User instruction: {instruction}\n"
                f"Topic: {topic}\n"
                f"Research context:\n{research_summary}\n\n"
                f"{_reference_context(reference_links)}\n\n"
                f"Current post:\n{current_draft}\n\n"
                "Revise the actual post instead of writing from scratch. Keep it professional, engaging, and platform-native. "
                "Include verified reference links when requested. Return only the revised post and never repeat prompt labels, "
                "review instructions, or conversation history."
            ),
            system="You are a LinkedIn editor refining an existing post.",
            temperature=0.5,
        )
    else:
        refined = (
            current_draft.rstrip()
            + f"\n\nRefinement request applied: {instruction}"
        )
    refined = _append_requested_references(refined, instruction, reference_links)

    return optimize_linkedin_post(
        refined,
        topic=topic,
        research_summary=research_summary,
        include_hashtags=include_hashtags,
        hashtag_count=hashtag_count,
    )
