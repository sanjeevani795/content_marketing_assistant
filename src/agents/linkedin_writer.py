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
