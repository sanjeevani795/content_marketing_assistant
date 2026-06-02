import os
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

try:
    import langsmith as ls
    from langsmith import traceable as _traceable
    from langsmith.wrappers import wrap_openai as _wrap_openai
except Exception:  # pragma: no cover
    ls = None
    _traceable = None
    _wrap_openai = None


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def tracing_enabled() -> bool:
    return bool(ls and _truthy_env("LANGSMITH_TRACING") and os.getenv("LANGSMITH_API_KEY"))


def langsmith_project_name() -> str:
    return os.getenv("LANGSMITH_PROJECT", "content-marketing-assistant")


def traceable(*args: Any, **kwargs: Any):
    if _traceable is None:
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]

        def decorator(func: F) -> F:
            return func

        return decorator

    return _traceable(*args, **kwargs)


def maybe_wrap_openai(client: Any) -> Any:
    if client is None or _wrap_openai is None or not tracing_enabled():
        return client
    return _wrap_openai(client)


@contextmanager
def tracing_session(
    run_name: str,
    metadata: Optional[dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
) -> Iterator[Optional[dict[str, Any]]]:
    if ls is None or not tracing_enabled():
        yield None
        return

    with ls.tracing_context(enabled=True, project_name=langsmith_project_name()):
        yield {
            "run_name": run_name,
            "tags": tags or [],
            "metadata": metadata or {},
        }
