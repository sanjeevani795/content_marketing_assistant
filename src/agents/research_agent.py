from datetime import datetime

from src.integrations.perplexity_client import PerplexityClient
from src.integrations.serp_client import SerpClient
from src.integrations.openai_client import OpenAIClient


def _local_research_fallback(query: str) -> dict:
    topic_tokens = [t for t in query.replace(",", " ").split() if len(t) > 4][:6]
    key_themes = topic_tokens or ["audience", "positioning", "distribution", "conversion"]
    findings = [
        f"Trend: {key_themes[0]} is becoming a primary growth lever.",
        "Audience expectation: practical, proof-backed content performs better than generic thought leadership.",
        "Execution: repurpose one research artifact into blog + social + visual variants for efficiency.",
    ]
    return {
        "query": query,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": "Local research fallback used because search providers are unavailable.",
        "findings": findings,
        "sources": [
            {
                "title": "Internal fallback synthesis",
                "url": "",
                "snippet": "Generated without external APIs.",
            }
        ],
        "provider": "local_fallback",
    }


def run_research(query: str) -> dict:
    serp = SerpClient()
    pplx = PerplexityClient()
    llm = OpenAIClient()

    try:
        if serp.enabled:
            sources = serp.search(query, max_results=6)
            source_text = "\n".join(f"- {s['title']}: {s['snippet']}" for s in sources)
            if llm.enabled:
                summary = llm.generate(
                    prompt=(
                        f"Create a concise research summary for this topic: {query}.\n"
                        f"Use these source snippets:\n{source_text}\n"
                        "Return: key insights, audience implications, and content opportunities."
                    ),
                    system="You are a research analyst for marketing teams.",
                )
            else:
                summary = "Research results collected; LLM summarization unavailable so raw themes are provided."
            return {
                "query": query,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "summary": summary,
                "findings": [s.get("snippet", "") for s in sources if s.get("snippet")],
                "sources": sources,
                "provider": "serpapi",
            }

        if pplx.enabled:
            response = pplx.ask(f"Provide deep research with practical citations on: {query}")
            return {
                "query": query,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "summary": response["answer"],
                "findings": [],
                "sources": [],
                "provider": "perplexity",
            }
    except Exception as exc:
        return {
            **_local_research_fallback(query),
            "error": f"Research provider error: {exc}",
        }

    return _local_research_fallback(query)
