import os
from urllib.parse import urlencode

import requests


class SerpClient:
    def __init__(self):
        self.api_key = os.getenv("SERP_API_KEY")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        if not self.enabled:
            raise RuntimeError("SERP API key not configured")

        params = {
            "engine": "google",
            "q": query,
            "num": max_results,
            "api_key": self.api_key,
        }
        url = f"https://serpapi.com/search.json?{urlencode(params)}"
        response = requests.get(url, timeout=25)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("organic_results", [])[:max_results]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
            )
        return results
