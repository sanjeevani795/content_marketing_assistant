from src.integrations.openai_client import OpenAIClient


def _hashtags(topic: str) -> list[str]:
    base = ["#Marketing", "#ContentStrategy", "#AI"]
    topic_tag = "#" + "".join(ch for ch in topic.title() if ch.isalnum())[:24]
    return [topic_tag] + base


def write_linkedin_post(topic: str, research_summary: str, include_hashtags: bool = True) -> str:
    llm = OpenAIClient()

    if llm.enabled:
        post = llm.generate(
            prompt=(
                f"Write a high-engagement LinkedIn post on: {topic}.\n"
                f"Context:\n{research_summary}\n"
                "Use: strong hook, short paragraphs, one tactical takeaway, and one question at the end."
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

    if include_hashtags:
        post = post.rstrip() + "\n\n" + " ".join(_hashtags(topic))
    return post
