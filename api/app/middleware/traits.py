from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable, Iterable

from fastapi import HTTPException

from ..config import providerHasTrait


def requires_traits(direction: str, keys: Iterable[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    strict = os.getenv("TRAITS_STRICT", "false").lower() in {"1", "true", "yes"}

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any):
            missing = [k for k in keys if not providerHasTrait(direction, k)]
            if missing:
                if strict:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "code": "capability_missing",
                            "required": missing,
                            "direction": direction,
                        },
                    )
                else:
                    # Warn‑only mode; proceed
                    # NOTE: real logging hook can be added here
                    pass
            return await fn(*args, **kwargs)

        return wrapper

    return decorator


