from typing import Any, Optional

from src.core.observability import traceable, tracing_session
from src.workflow.langgraph_workflow import build_workflow

workflow = build_workflow()


@traceable(name="content_marketing_workflow", run_type="chain")
def run_workflow(
    user_query: str,
    chat_history: Optional[list[dict[str, str]]] = None,
    prior_run: Optional[dict[str, Any]] = None,
):
    payload = {
        "user_query": user_query,
        "chat_history": chat_history or [],
        "prior_route": (prior_run or {}).get("route", ""),
        "prior_outputs": (prior_run or {}).get("outputs", {}),
        "errors": [],
        "node_status": {},
    }
    metadata = {
        "history_turns": len(chat_history or []),
        "query_length": len(user_query),
    }

    with tracing_session(
        run_name="content_marketing_workflow",
        metadata=metadata,
        tags=["content-marketing", "langgraph"],
    ) as trace_config:
        if trace_config:
            return workflow.invoke(payload, config=trace_config)
        return workflow.invoke(payload)
