from typing import Any, Optional

from src.core.workflow import run_workflow


def handle_query(
    user_query: str,
    chat_history: Optional[list[dict[str, str]]] = None,
    prior_run: Optional[dict[str, Any]] = None,
):
    return run_workflow(
        user_query=user_query,
        chat_history=chat_history,
        prior_run=prior_run,
    )
