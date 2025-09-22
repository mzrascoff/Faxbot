from __future__ import annotations
from functools import wraps
from typing import Callable, Iterable
import os
from fastapi import HTTPException
from .config import providerHasTrait

TRAITS_STRICT = os.getenv("TRAITS_STRICT", "false").lower() in {"1","true","yes"}


def requires_traits(direction: str, keys: Iterable[str]) -> Callable:
    """Decorator to enforce provider traits at runtime.

    On violation:
      - When TRAITS_STRICT=true → raise 400 capability_missing with details
      - Otherwise: allow but do nothing (compatibility), callers can log warning
    """

    kset = set(keys or [])

    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def _inner(*args, **kwargs):
            missing = [k for k in kset if not bool(providerHasTrait(direction, k))]
            if missing and TRAITS_STRICT:
                raise HTTPException(status_code=400, detail={
                    "code": "capability_missing",
                    "direction": direction,
                    "required": missing,
                })
            return func(*args, **kwargs)

        return _inner

    return _decorator

