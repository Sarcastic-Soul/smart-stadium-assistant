"""Security utilities – rate limiting, API-key retrieval, input sanitisation.

In production the API key is fetched from GCP Secret Manager via the
Secret Manager CSI driver (mounted at /secrets/CLONEMODEL_API_KEY).
In development it falls back to the CLONEMODEL_API_KEY environment variable.
"""

from __future__ import annotations

import logging
import os
import re
from functools import lru_cache
from pathlib import Path

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

_SECRET_MOUNT_PATH = Path("/secrets/CLONEMODEL_API_KEY")


@lru_cache(maxsize=1)
def get_api_key() -> str:
    """Return the LLM provider API key.

    Resolution order:
    1. Kubernetes Secret Manager CSI volume mount.
    2. Environment variable ``CLONEMODEL_API_KEY``.
    3. Empty string (tests / local dev without a key).
    """
    # 1. CSI volume mount (production on GKE)
    if _SECRET_MOUNT_PATH.exists():
        key = _SECRET_MOUNT_PATH.read_text().strip()
        if key:
            logger.info("API key loaded from Secret Manager CSI mount.")
            return key

    # 2. Environment variable (local development)
    env_key = os.getenv("CLONEMODEL_API_KEY", "")
    if env_key:
        logger.info("API key loaded from environment variable.")
        return env_key

    logger.warning(
        "No API key found – LLM calls will use simulated responses."
    )
    return ""
