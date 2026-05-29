def format_content_package(
    topic: str,
    research: dict,
    blog: str | None = None,
    linkedin: str | None = None,
    image: dict | None = None,
) -> dict:
    return {
        "topic": topic,
        "research_report": research,
        "seo_blog": blog,
        "linkedin_post": linkedin,
        "image_asset": image,
        "delivery_notes": [
            "Use research summary as campaign anchor.",
            "Repurpose blog sections into LinkedIn carousel/script.",
            "Pair image with blog hero and social teaser variants.",
        ],
    }
