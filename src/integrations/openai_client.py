import os
from typing import Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class OpenAIClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if (OpenAI and self.api_key) else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.4) -> str:
        if not self.enabled:
            raise RuntimeError("OpenAI is not configured")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def generate_image(self, prompt: str, size: str = "1024x1024") -> str:
        if not self.enabled:
            raise RuntimeError("OpenAI is not configured")
        image = self.client.images.generate(model="gpt-image-1", prompt=prompt, size=size)
        # gpt-image-1 can return base64 content in b64_json and/or URL depending on SDK version.
        data = image.data[0]
        if getattr(data, "url", None):
            return data.url
        if getattr(data, "b64_json", None):
            return f"data:image/png;base64,{data.b64_json}"
        raise RuntimeError("No image payload returned")
