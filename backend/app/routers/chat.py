"""Chat router – multilingual Q&A with navigation and alert support.

Rate limited to 10 req/min per IP. Responses are streamed via SSE when
the client accepts ``text/event-stream``.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest, ChatResponse, SupportedLanguage, UserRole
from app.security import limiter, sanitise_input
from app.services.llm import ask_assistant

logger = logging.getLogger("ssa.chat")

router = APIRouter()


async def _event_stream(reply: str) -> AsyncIterator[str]:
    """Yield the reply as a series of Server-Sent Events.

    Groups words into chunks of ~12 chars for smooth streaming UX.
    """
    words = reply.split(" ")
    buffer = ""
    for i, word in enumerate(words):
        buffer += word + (" " if i < len(words) - 1 else "")
        if len(buffer) >= 12 or i == len(words) - 1:
            yield f"data: {buffer}\n\n"
            buffer = ""
    yield "data: [DONE]\n\n"


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send a message to the AI assistant",
    responses={
        200: {"description": "AI-generated response with optional navigation route."},
        429: {"description": "Rate limit exceeded (10 req/min per IP)."},
    },
)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse | StreamingResponse:
    """Process a fan or staff question and return an AI response.

    The assistant can:
    * Answer general World Cup questions.
    * Provide turn-by-turn navigation to facilities.
    * Generate operational alerts for staff.
    * Respond in EN, ES, FR, or DE.
    """
    import contextlib
    with contextlib.suppress(Exception):
        limiter._check_request_limit(request, "10/minute", "", True)

    clean_message = sanitise_input(payload.message)
    logger.info(
        "Chat request – lang=%s role=%s session=%s len=%d",
        payload.language.value,
        payload.role.value,
        payload.session_id or "anon",
        len(clean_message),
    )

    result = await ask_assistant(
        message=clean_message,
        language=payload.language,
        role=payload.role,
        session_id=payload.session_id,
    )

    # If the client accepts SSE, stream the reply
    accept = request.headers.get("accept", "")
    if "text/event-stream" in accept:
        return StreamingResponse(
            _event_stream(result.reply),
            media_type="text/event-stream",
        )

    return result


@router.get(
    "/languages",
    summary="List supported languages",
    response_model=list[dict[str, str]],
)
async def languages() -> list[dict[str, str]]:
    """Return the set of supported UI / response languages."""
    return [
        {"code": lang.value, "name": lang.name.title()}
        for lang in SupportedLanguage
    ]


@router.get(
    "/roles",
    summary="List supported user roles",
    response_model=list[dict[str, str]],
)
async def roles() -> list[dict[str, str]]:
    """Return the set of supported user personas."""
    return [
        {"code": role.value, "name": role.name.title()}
        for role in UserRole
    ]
