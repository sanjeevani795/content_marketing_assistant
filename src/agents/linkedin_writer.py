from src.integrations.openai_client import OpenAIClient
from src.core.observability import traceable
from src.utils.content_optimization import optimize_linkedin_post


@traceable(name="linkedin_post_writer_agent", run_type="chain")
def write_linkedin_post(topic: str, research_summary: str, include_hashtags: bool = True) -> str:
    llm = OpenAIClient()

    if llm.enabled:
        post = llm.generate(
            prompt=(
                f"Write a high-engagement LinkedIn post on: {topic}.\n"
                f"Context:\n{research_summary}\n"
                "Use: strong hook, short paragraphs, one tactical takeaway, a clear CTA question, "
                "professional tone with personality, and line breaks that feel easy to scan on mobile."
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

    return optimize_linkedin_post(
        post,
        topic=topic,
        research_summary=research_summary,
        include_hashtags=include_hashtags,
    )


@traceable(name="linkedin_post_refinement_agent", run_type="chain")
def refine_linkedin_post(
    current_draft: str,
    instruction: str,
    topic: str,
    research_summary: str,
    include_hashtags: bool = True,
) -> str:
    llm = OpenAIClient()

    if llm.enabled:
        refined = llm.generate(
            prompt=(
                f"Refine this existing LinkedIn post based on the user instruction.\n"
                f"User instruction: {instruction}\n"
                f"Topic: {topic}\n"
                f"Research context:\n{research_summary}\n\n"
                f"Current post:\n{current_draft}\n\n"
                "Revise the actual post instead of writing from scratch. Keep it professional, engaging, and platform-native."
            ),
            system="You are a LinkedIn editor refining an existing post.",
            temperature=0.5,
        )
    else:
        refined = (
            current_draft.rstrip()
            + f"\n\nRefinement request applied: {instruction}"
        )

    return optimize_linkedin_post(
        refined,
        topic=topic,
        research_summary=research_summary,
        include_hashtags=include_hashtags,
    )
