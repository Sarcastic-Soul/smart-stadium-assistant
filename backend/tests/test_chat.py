"""Tests for the Chat router and LLM service.

Covers:
- Health endpoints
- Chat endpoint validation & rate limiting
- Language listing
- Simulated LLM responses for navigation and Q&A
- Input sanitisation
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas import SupportedLanguage
from app.security import sanitise_input
from app.services.llm import _build_simulated_reply, _detect_facility

# ── Fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Yield an async test client bound to the app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Health Probes ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_healthz(client: AsyncClient) -> None:
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_readyz(client: AsyncClient) -> None:
    resp = await client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}


# ── Chat Endpoint ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_chat_basic(client: AsyncClient) -> None:
    """A simple chat request should return a 200 with a reply."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello, where can I find food?", "language": "en"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["language"] == "en"


@pytest.mark.anyio
async def test_chat_navigation(client: AsyncClient) -> None:
    """Asking for a restroom should return a route with waypoints."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "Where is the nearest restroom?", "language": "en"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("route") is not None
    assert len(data["route"]["waypoints"]) > 0
    assert data["route"]["eta_minutes"] is not None


@pytest.mark.anyio
async def test_chat_spanish(client: AsyncClient) -> None:
    """Spanish language request should return a Spanish reply."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "¿Dónde está el baño?", "language": "es"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "es"


@pytest.mark.anyio
async def test_chat_empty_message(client: AsyncClient) -> None:
    """An empty message should be rejected (422)."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "", "language": "en"},
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_chat_message_too_long(client: AsyncClient) -> None:
    """A message exceeding max length should be rejected (422)."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "x" * 2001, "language": "en"},
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_chat_invalid_language(client: AsyncClient) -> None:
    """An unsupported language code should be rejected."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello", "language": "zz"},
    )
    assert resp.status_code == 422


# ── Language Listing ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_languages(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/chat/languages")
    assert resp.status_code == 200
    langs = resp.json()
    assert len(langs) == 4
    codes = {lang["code"] for lang in langs}
    assert codes == {"en", "es", "fr", "de"}


# ── Sensor Endpoints ────────────────────────────────────────────

@pytest.mark.anyio
async def test_sensor_snapshot(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sensors/snapshot")
    assert resp.status_code == 200
    data = resp.json()
    assert "crowd" in data
    assert "sustainability" in data
    assert "alerts" in data
    assert len(data["crowd"]) == 10  # 10 zones


@pytest.mark.anyio
async def test_sensor_crowd(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sensors/crowd")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert all("density_pct" in z for z in data)


@pytest.mark.anyio
async def test_sensor_sustainability(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sensors/sustainability")
    assert resp.status_code == 200
    data = resp.json()
    assert "energy_kwh" in data
    assert "recycling_rate_pct" in data


@pytest.mark.anyio
async def test_sensor_alerts(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sensors/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert 2 <= len(data) <= 4


@pytest.mark.anyio
async def test_sensor_zones(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/sensors/zones")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 10


# ── Unit Tests: LLM Service ─────────────────────────────────────

def test_detect_facility_restroom() -> None:
    assert _detect_facility("Where is the restroom?") == "restroom"


def test_detect_facility_bathroom_alias() -> None:
    assert _detect_facility("I need a bathroom") == "restroom"


def test_detect_facility_food() -> None:
    assert _detect_facility("Where can I eat?") == "food"


def test_detect_facility_exit() -> None:
    assert _detect_facility("How do I leave the stadium?") == "exit"


def test_detect_facility_none() -> None:
    assert _detect_facility("What time is kickoff?") is None


def test_simulated_reply_navigation() -> None:
    result = _build_simulated_reply("Where is the restroom?", SupportedLanguage.EN)
    assert result.route is not None
    assert len(result.route.waypoints) > 0
    assert "restroom" in result.reply.lower() or "route" in result.reply.lower()


def test_simulated_reply_general() -> None:
    result = _build_simulated_reply("Hello!", SupportedLanguage.EN)
    assert result.route is None
    assert "World Cup" in result.reply


def test_simulated_reply_spanish() -> None:
    result = _build_simulated_reply("Hola", SupportedLanguage.ES)
    assert result.language == SupportedLanguage.ES
    assert "🇪🇸" in result.reply


def test_simulated_reply_french() -> None:
    result = _build_simulated_reply("Bonjour", SupportedLanguage.FR)
    assert result.language == SupportedLanguage.FR


def test_simulated_reply_german() -> None:
    result = _build_simulated_reply("Hallo", SupportedLanguage.DE)
    assert result.language == SupportedLanguage.DE


# ── Unit Tests: Security ─────────────────────────────────────────

def test_sanitise_removes_script_tags() -> None:
    assert "<script" not in sanitise_input("<script>alert('xss')</script>")


def test_sanitise_removes_event_handlers() -> None:
    assert "onerror" not in sanitise_input('<img onerror="alert(1)">')


def test_sanitise_preserves_normal_text() -> None:
    assert sanitise_input("Where is Gate 4?") == "Where is Gate 4?"


def test_sanitise_strips_whitespace() -> None:
    assert sanitise_input("  hello  ") == "hello"


@pytest.mark.anyio
async def test_chat_sse_streaming(client: AsyncClient) -> None:
    """Test Server-Sent Events stream."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello"},
        headers={"accept": "text/event-stream"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "text/event-stream; charset=utf-8"
    content = resp.read().decode()
    assert "data: " in content
    assert "[DONE]" in content


@pytest.mark.anyio
async def test_chat_roles(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/chat/roles")
    assert resp.status_code == 200
    roles = resp.json()
    assert any(r["code"] == "staff" for r in roles)


@pytest.mark.anyio
async def test_chat_session(client: AsyncClient) -> None:
    """Session IDs should be accepted and stored in history."""
    resp = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello", "session_id": "test_session_123", "role": "staff"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Live Status" in data["reply"]


@pytest.mark.anyio
async def test_simulated_reply_roles() -> None:
    from app.schemas import UserRole
    result = _build_simulated_reply("Hello!", SupportedLanguage.EN, role=UserRole.STAFF)
    assert "Live Status" in result.reply

    result2 = _build_simulated_reply("Hello!", SupportedLanguage.EN, role=UserRole.FAN)
    assert "Live Status" not in result2.reply


def test_detect_facility_accessible() -> None:
    assert _detect_facility("Where is the wheelchair ramp?") == "accessible"


def test_detect_facility_parking() -> None:
    assert _detect_facility("Where is the shuttle?") == "parking"
