from langgraph.graph import END, StateGraph

from src.agents.blog_writer import write_blog
from src.agents.content_strategist import format_content_package
from src.agents.image_generator import generate_image
from src.agents.linkedin_writer import write_linkedin_post
from src.agents.research_agent import run_research
from src.core.router import infer_intent
from src.utils.content_optimization import extract_keywords
from src.utils.quality_validation import evaluate_outputs
from src.workflow.state_management import WorkflowState


def route_node(state: WorkflowState) -> WorkflowState:
    route, scores = infer_intent(state["user_query"])
    state["route"] = route
    state["intent_scores"] = scores
    state["keywords"] = extract_keywords(state["user_query"])
    state["topic"] = state["user_query"]
    return state


def research_node(state: WorkflowState) -> WorkflowState:
    state["research"] = run_research(state["topic"])
    state["outputs"] = {"research_report": state["research"]}
    return state


def blog_node(state: WorkflowState) -> WorkflowState:
    research = state.get("research") or run_research(state["topic"])
    state["research"] = research
    state["blog_draft"] = write_blog(
        topic=state["topic"],
        research_summary=research.get("summary", ""),
        keywords=state.get("keywords", []),
    )
    state["outputs"] = {
        "research_report": research,
        "seo_blog": state["blog_draft"],
    }
    return state


def linkedin_node(state: WorkflowState) -> WorkflowState:
    research = state.get("research") or run_research(state["topic"])
    state["research"] = research
    state["linkedin_draft"] = write_linkedin_post(
        topic=state["topic"], research_summary=research.get("summary", "")
    )
    state["outputs"] = {
        "research_report": research,
        "linkedin_post": state["linkedin_draft"],
    }
    return state


def image_node(state: WorkflowState) -> WorkflowState:
    image = generate_image(topic=state["topic"])
    state["image_prompt"] = image["prompt"]
    state["image_output"] = image["image"]
    state["outputs"] = {
        "image_asset": image,
    }
    return state


def strategy_node(state: WorkflowState) -> WorkflowState:
    research = run_research(state["topic"])
    blog = write_blog(state["topic"], research.get("summary", ""), state.get("keywords", []))
    linkedin = write_linkedin_post(state["topic"], research.get("summary", ""))
    image = generate_image(state["topic"])

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
    return state


def quality_node(state: WorkflowState) -> WorkflowState:
    state["quality"] = evaluate_outputs(state.get("outputs", {}))
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
