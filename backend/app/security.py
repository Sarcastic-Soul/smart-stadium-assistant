"""Security utilities – rate limiting, API-key retrieval, input sanitisation.

In production on Vercel the API key is retrieved via the GROQ_API_KEY environment variable.
In development it falls back to the GROQ_API_KEY environment variable.
"""

from __future__ import annotations

import logging
import os
import re
from functools import lru_cache

from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger("ssa.security")

# ── Rate Limiter ─────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri="memory://",
)

# ── Dangerous-pattern filter ────────────────────────────────────
_INJECTION_PATTERNS = re.compile(
    r"(<script|javascript:|on\w+=|data:text/html|eval\(|document\.)",
    re.IGNORECASE,
)


def sanitise_input(text: str) -> str:
    """Strip potential XSS / injection patterns from user text."""
    return _INJECTION_PATTERNS.sub("", text).strip()


# ── API Key Retrieval ────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_api_key() -> str:
    """Return the LLM provider API key from the environment.

    Resolution order:
    1. Environment variable ``GROQ_API_KEY``.
    2. Empty string (tests / local dev without a key).
    """
    env_key = os.getenv("GROQ_API_KEY", "")
    if env_key:
        logger.debug("GROQ API key loaded from environment variable.")
        return env_key

    logger.warning(
        "No GROQ_API_KEY found – LLM calls will use simulated responses."
    )
    return ""
