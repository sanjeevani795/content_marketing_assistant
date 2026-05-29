from src.workflow.langgraph_workflow import build_workflow

workflow = build_workflow()


def run_workflow(user_query: str, chat_history: list[dict[str, str]] | None = None):
    return workflow.invoke(
        {
            "user_query": user_query,
            "chat_history": chat_history or [],
            "errors": [],
        }
    )
