from typing import Optional

from src.core.workflow import run_workflow


def handle_query(
    user_query: str, chat_history: Optional[list[dict[str, str]]] = None
):
    return run_workflow(user_query=user_query, chat_history=chat_history)
