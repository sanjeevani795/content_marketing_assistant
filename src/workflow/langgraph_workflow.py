from datetime import datetime

from langgraph.graph import END, StateGraph

from src.agents.blog_writer import write_blog
from src.agents.content_strategist import format_content_package
from src.agents.image_generator import generate_image
from src.agents.linkedin_writer import write_linkedin_post
from src.agents.research_agent import run_research
from src.core.observability import traceable
from src.core.router import build_topic, infer_intent
from src.utils.content_optimization import extract_keywords
from src.utils.quality_validation import evaluate_outputs
from src.workflow.state_management import WorkflowState


def _record_node_status(state: WorkflowState, node_name: str, status: str) -> None:
    node_status = state.setdefault("node_status", {})
    node_status[node_name] = status


def _record_error(state: WorkflowState, node_name: str, exc: Exception) -> None:
    errors = state.setdefault("errors", [])
    errors.append(f"{node_name}: {exc}")
    _record_node_status(state, node_name, "fallback")


def _fallback_research(topic: str, reason: str) -> dict:
    return {
        "query": topic,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": "Research fallback used because the primary research step failed.",
        "findings": [
            "Fallback mode preserved workflow continuity.",
            "Use follow-up research once provider connectivity is restored.",
        ],
        "sources": [],
        "provider": "workflow_fallback",
        "error": reason,
    }


def _fallback_blog(topic: str, research_summary: str, keywords: list[str]) -> str:
    primary = keywords[0] if keywords else topic
    return (
        f"# {topic}\n\n"
        "## Overview\n"
        f"{research_summary[:300] or 'A fallback blog draft was created because the primary writer failed.'}\n\n"
        "## Key Takeaways\n"
        "- Focus on one audience problem.\n"
        "- Support claims with concrete examples.\n"
        "- End with a clear next step.\n\n"
        f"Meta Description: Practical guide to {primary} with actionable structure and positioning advice."
    )


def _fallback_linkedin(topic: str, research_summary: str) -> str:
    return (
        f"Strong content systems are built on clear positioning, not more posting.\n\n"
        f"Topic: {topic}\n"
        f"Context: {research_summary[:220] or 'Fallback copy generated after a writer error.'}\n\n"
        "What would improve first if your team reused one solid research asset across formats?\n\n"
        "#Marketing #ContentStrategy #AI"
    )


def _fallback_image(topic: str, prompt: str, reason: str) -> dict:
    return {
        "prompt": prompt,
        "image": "https://placehold.co/1024x1024/png?text=Image+Fallback",
        "provider": "workflow_fallback",
        "error": reason,
        "topic": topic,
    }


def _get_research(state: WorkflowState) -> tuple[dict, str]:
    if state.get("research"):
        return state["research"], "ok"

    try:
        research = run_research(state["topic"])
        return research, "ok"
    except Exception as exc:
        _record_error(state, "research", exc)
        return _fallback_research(state["topic"], str(exc)), "fallback"


def _get_blog(state: WorkflowState, research_summary: str) -> tuple[str, str]:
    try:
        return (
            write_blog(
                topic=state["topic"],
                research_summary=research_summary,
                keywords=state.get("keywords", []),
            ),
            "ok",
        )
    except Exception as exc:
        _record_error(state, "blog", exc)
        return (
            _fallback_blog(state["topic"], research_summary, state.get("keywords", [])),
            "fallback",
        )


def _get_linkedin(state: WorkflowState, research_summary: str) -> tuple[str, str]:
    try:
        return (
            write_linkedin_post(topic=state["topic"], research_summary=research_summary),
            "ok",
        )
    except Exception as exc:
        _record_error(state, "linkedin", exc)
        return _fallback_linkedin(state["topic"], research_summary), "fallback"


def _get_image(state: WorkflowState) -> tuple[dict, str]:
    prompt = f"Create a high-quality marketing illustration about '{state['topic']}'."
    try:
        image = generate_image(topic=state["topic"])
        return image, "ok"
    except Exception as exc:
        _record_error(state, "image", exc)
        return _fallback_image(state["topic"], prompt, str(exc)), "fallback"


@traceable(name="route_node", run_type="chain")
def route_node(state: WorkflowState) -> WorkflowState:
    try:
        route, scores, routing_details = infer_intent(
            state["user_query"], chat_history=state.get("chat_history")
        )
        state["route"] = route
        state["route_source"] = routing_details["route_source"]
        state["routing_details"] = routing_details
        state["ambiguity_detected"] = routing_details["ambiguous"]
        state["intent_scores"] = scores
        state["keywords"] = extract_keywords(state["user_query"])
        state["topic"] = build_topic(state["user_query"], chat_history=state.get("chat_history"))
        _record_node_status(state, "route", "ok")
    except Exception as exc:
        state["route"] = "research"
        state["route_source"] = "routing_error_fallback"
        state["routing_details"] = {"error": str(exc), "route_source": "routing_error_fallback"}
        state["ambiguity_detected"] = True
        state["intent_scores"] = {}
        state["keywords"] = extract_keywords(state["user_query"])
        state["topic"] = state["user_query"]
        _record_error(state, "route", exc)
    return state


@traceable(name="research_node", run_type="chain")
def research_node(state: WorkflowState) -> WorkflowState:
    research, status = _get_research(state)
    state["research"] = research
    state["outputs"] = {"research_report": state["research"]}
    _record_node_status(state, "research", status)
    return state


@traceable(name="blog_node", run_type="chain")
def blog_node(state: WorkflowState) -> WorkflowState:
    research, research_status = _get_research(state)
    state["research"] = research
    state["blog_draft"], blog_status = _get_blog(state, research.get("summary", ""))
    state["outputs"] = {
        "research_report": research,
        "seo_blog": state["blog_draft"],
    }
    _record_node_status(state, "research", research_status)
    _record_node_status(state, "blog", blog_status)
    return state


@traceable(name="linkedin_node", run_type="chain")
def linkedin_node(state: WorkflowState) -> WorkflowState:
    research, research_status = _get_research(state)
    state["research"] = research
    state["linkedin_draft"], linkedin_status = _get_linkedin(
        state, research.get("summary", "")
    )
    state["outputs"] = {
        "research_report": research,
        "linkedin_post": state["linkedin_draft"],
    }
    _record_node_status(state, "research", research_status)
    _record_node_status(state, "linkedin", linkedin_status)
    return state


@traceable(name="image_node", run_type="chain")
def image_node(state: WorkflowState) -> WorkflowState:
    image, status = _get_image(state)
    state["image_prompt"] = image["prompt"]
    state["image_output"] = image["image"]
    state["outputs"] = {
        "image_asset": image,
    }
    _record_node_status(state, "image", status)
    return state


@traceable(name="strategy_node", run_type="chain")
def strategy_node(state: WorkflowState) -> WorkflowState:
    research, research_status = _get_research(state)
    blog, blog_status = _get_blog(state, research.get("summary", ""))
    linkedin, linkedin_status = _get_linkedin(state, research.get("summary", ""))
    image, image_status = _get_image(state)

    state["research"] = research
    state["blog_draft"] = blog
    state["linkedin_draft"] = linkedin
    state["image_prompt"] = image["prompt"]
    state["image_output"] = image["image"]

    state["outputs"] = format_content_package(
        topic=state["topic"],
        research=research,
        blog=blog,
        linkedin=linkedin,
        image=image,
    )
    _record_node_status(state, "research", research_status)
    _record_node_status(state, "blog", blog_status)
    _record_node_status(state, "linkedin", linkedin_status)
    _record_node_status(state, "image", image_status)
    _record_node_status(state, "strategy", "ok")
    return state


@traceable(name="quality_node", run_type="chain")
def quality_node(state: WorkflowState) -> WorkflowState:
    try:
        state["quality"] = evaluate_outputs(
            state.get("outputs", {}), errors=state.get("errors", [])
        )
        _record_node_status(state, "quality", "ok")
    except Exception as exc:
        _record_error(state, "quality", exc)
        state["quality"] = {
            "scores": {"blog": 0.0, "linkedin": 0.0, "research": 0.0, "overall": 0.0},
            "improvements": ["Quality evaluation failed, so the outputs should be reviewed manually."],
            "errors": state.get("errors", []),
        }
    return state


def build_workflow():
    graph = StateGraph(WorkflowState)
    graph.add_node("route", route_node)
    graph.add_node("research", research_node)
    graph.add_node("blog", blog_node)
    graph.add_node("linkedin", linkedin_node)
    graph.add_node("image", image_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("quality", quality_node)

    graph.set_entry_point("route")
    graph.add_conditional_edges(
        "route",
        lambda s: s["route"],
        {
            "research": "research",
            "blog": "blog",
            "linkedin": "linkedin",
            "image": "image",
            "strategy": "strategy",
        },
    )

    for node in ["research", "blog", "linkedin", "image", "strategy"]:
        graph.add_edge(node, "quality")
    graph.add_edge("quality", END)

    return graph.compile()
