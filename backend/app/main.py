"""Smart Stadium Assistant – FastAPI Entry Point.

Provides the main application factory and startup/shutdown lifecycle hooks.
All routes are mounted from the routers package.
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import chat, sensors
from app.security import limiter


def _configure_logging() -> None:
    """Set up structured logging with consistent format."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


logger = logging.getLogger("ssa")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security headers into every response."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        """Add security headers to the response."""
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(self)"
        )
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan – run startup & shutdown logic."""
    _configure_logging()
    logger.info("Smart Stadium Assistant v1.0.0 starting up …")
    logger.info("Environment: %s", os.getenv("APP_ENV", "development"))
    yield
    logger.info("Smart Stadium Assistant shutting down …")


def create_app() -> FastAPI:
    """Application factory – returns a fully configured FastAPI instance."""
    app_env = os.getenv("APP_ENV", "development")

    app = FastAPI(
        title="Smart Stadium Assistant",
        description=(
            "Generative-AI-driven assistant for FIFA World Cup 2026 "
            "tournament operations – navigation, crowd analytics, "
            "sustainability metrics, multilingual Q&A, and operational alerts."
        ),
        version="1.0.0",
        docs_url="/docs" if app_env == "development" else None,
        redoc_url="/redoc" if app_env == "development" else None,
        lifespan=lifespan,
    )

    # ── Security Headers ─────────────────────────────────────────
    app.add_middleware(SecurityHeadersMiddleware)

    # ── Rate Limiter ─────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── CORS ─────────────────────────────────────────────────────
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
        max_age=600,
    )

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["Sensors"])

    # ── Health Check ─────────────────────────────────────────────
    @app.get("/healthz", tags=["Health"])
    async def healthz() -> dict[str, str]:
        """Liveness probe for Kubernetes."""
        return {"status": "ok"}

    @app.get("/readyz", tags=["Health"])
    async def readyz() -> dict[str, str]:
        """Readiness probe for Kubernetes."""
        return {"status": "ready"}

    return app


app = create_app()
