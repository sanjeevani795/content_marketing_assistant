from src.integrations.openai_client import OpenAIClient


class ImageClient:
    def __init__(self):
        self.openai = OpenAIClient()

    def generate(self, prompt: str) -> str:
        if self.openai.enabled:
            return self.openai.generate_image(prompt)

        # Fallback: return a shareable placeholder image URL with text context.
        return "https://placehold.co/1024x1024/png?text=Generated+Image+Preview"
