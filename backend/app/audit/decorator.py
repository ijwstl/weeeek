from collections.abc import Callable
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any

from sqlalchemy.orm import Session


def audit_log(
    action: str,
    resource_type: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Lightweight audit marker.

    The first implementation stores metadata on the wrapper. The real recorder
    will be wired after auth, request context, and audit tables are in place.
    """

    def outer(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)
            record_success(action, resource_type, args, kwargs)
            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            record_success(action, resource_type, args, kwargs)
            return result

        wrapper = async_wrapper if iscoroutinefunction(func) else sync_wrapper
        wrapper.audit_action = action
        wrapper.audit_resource_type = resource_type
        return wrapper

    return outer


def record_success(
    action: str,
    resource_type: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> None:
    from app.services.audit import record_audit_log

    record_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=find_resource_id(kwargs),
        db=find_session(args, kwargs),
        metadata_json={"source": "audit_decorator"},
    )


def find_session(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Session | None:
    for value in [*kwargs.values(), *args]:
        if isinstance(value, Session):
            return value
    return None


def find_resource_id(kwargs: dict[str, Any]) -> str | None:
    for key, value in kwargs.items():
        if key.endswith("_id") or key in {"template_id", "channel_id"}:
            return str(value)
    return None
