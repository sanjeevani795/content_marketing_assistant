import os
import requests


class PerplexityClient:
    def __init__(self, model: str = "sonar"):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.model = model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def ask(self, query: str) -> dict:
        if not self.enabled:
            raise RuntimeError("Perplexity API key not configured")

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": query}],
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        answer = payload["choices"][0]["message"]["content"]
        return {"query": query, "answer": answer}
