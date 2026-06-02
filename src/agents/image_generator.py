from src.integrations.image_clients import ImageClient
from src.core.observability import traceable


def generate_image_prompt(topic: str, brand_voice: str = "professional") -> str:
    return (
        f"Create a high-quality marketing illustration about '{topic}'. "
        f"Style: {brand_voice}, modern editorial, clean composition, strong focal subject, "
        "brand-safe, no text overlays, web-hero friendly lighting."
    )


@traceable(name="image_generation_agent", run_type="chain")
def generate_image(topic: str, brand_voice: str = "professional") -> dict:
    prompt = generate_image_prompt(topic=topic, brand_voice=brand_voice)
    client = ImageClient()
    image_output = client.generate(prompt)
    return {"prompt": prompt, "image": image_output}
