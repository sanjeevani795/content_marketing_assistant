from src.integrations.image_clients import ImageClient


def generate_image_prompt(topic: str, brand_voice: str = "professional") -> str:
    return (
        f"Create a high-quality marketing illustration about '{topic}'. "
        f"Style: {brand_voice}, modern editorial, clean composition, strong focal subject, "
        "brand-safe, no text overlays, web-hero friendly lighting."
    )


def generate_image(topic: str, brand_voice: str = "professional") -> dict:
    prompt = generate_image_prompt(topic=topic, brand_voice=brand_voice)
    client = ImageClient()
    image_output = client.generate(prompt)
    return {"prompt": prompt, "image": image_output}
