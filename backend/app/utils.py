"""Shared utility functions for the backend application.

Contains reusable decorators and helpers used across multiple modules.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def ttl_cache(ttl_seconds: int = 10) -> Callable:
    """Synchronous time-to-live cache decorator.

    Caches the return value of the decorated function for ``ttl_seconds``.
    Subsequent calls within the TTL window return the cached result without
    re-executing the function.

    Args:
        ttl_seconds: Number of seconds to retain the cached value.

    Returns:
        A decorator that wraps the target function with TTL caching.
    """

    def decorator(func: Callable) -> Callable:
        cache: dict[str, Any] = {}

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            if "result" in cache and now - cache["timestamp"] < ttl_seconds:
                return cache["result"]
            result = func(*args, **kwargs)
            cache["result"] = result
            cache["timestamp"] = now
            return result

        return wrapper

    return decorator
