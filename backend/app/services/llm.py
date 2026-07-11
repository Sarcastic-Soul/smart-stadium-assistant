"""LLM service – interface to the Anthropic Claude API.

When an API key is available, real LLM calls are made.  Otherwise, a
deterministic simulator provides canned responses so the app remains
functional during demos and tests.

Features:
  - In-memory conversation history (per session)
  - Role-aware responses (fan / staff / volunteer / organizer)
  - Sensor-aware context injection for real-time decision support
  - Connection-pooled async HTTP client
  - Graceful fallback to simulator when no API key
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Optional

import httpx

from app.schemas import (
    ChatResponse,
    NavigationRoute,
    SupportedLanguage,
    UserRole,
    Waypoint,
)
from app.security import get_api_key
from app.services.simulators import generate_alerts, generate_crowd_density

logger = logging.getLogger("ssa.llm")

# ── Reusable async HTTP client (connection-pooled) ──────────────
_http_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    """Lazy-initialise a connection-pooled async HTTP client."""
    global _http_client  # noqa: PLW0603
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


# ── Session Memory (bounded per-session history) ────────────────
_MAX_HISTORY = 10
_session_history: dict[str, list[dict[str, str]]] = defaultdict(list)


def _get_history(session_id: Optional[str]) -> list[dict[str, str]]:
    """Return conversation history for a session (up to _MAX_HISTORY)."""
    if not session_id:
        return []
    return _session_history[session_id][-_MAX_HISTORY:]


def _append_history(
    session_id: Optional[str], role: str, content: str
) -> None:
    """Append a message to session history."""
    if session_id:
        _session_history[session_id].append({"role": role, "content": content})
        # Bound memory usage
        if len(_session_history[session_id]) > _MAX_HISTORY * 2:
            _session_history[session_id] = _session_history[session_id][
                -_MAX_HISTORY:
            ]


# ── Simulated facility coordinates (stadium floor-plan) ─────────
_FACILITY_COORDS: dict[str, list[Waypoint]] = {
    "restroom": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6540, lng=-80.2385, label="Turn left at Gate 4"),
        Waypoint(lat=25.6542, lng=-80.2380, label="Restroom 3A"),
    ],
    "food": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6535, lng=-80.2392, label="Concourse B"),
        Waypoint(lat=25.6533, lng=-80.2395, label="Food Court"),
    ],
    "exit": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6530, lng=-80.2400, label="Main Exit"),
    ],
    "first aid": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6545, lng=-80.2378, label="First Aid Station"),
    ],
    "vip": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6541, lng=-80.2375, label="VIP Entrance"),
        Waypoint(lat=25.6543, lng=-80.2372, label="VIP Lounge"),
    ],
    "parking": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6528, lng=-80.2405, label="Parking Lot A"),
    ],
    "merchandise": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6536, lng=-80.2393, label="Official Merchandise Store"),
    ],
    "accessible": [
        Waypoint(lat=25.6537, lng=-80.2389, label="You are here"),
        Waypoint(lat=25.6538, lng=-80.2387, label="Accessible Ramp A2"),
        Waypoint(lat=25.6540, lng=-80.2384, label="Elevator – Level 2"),
        Waypoint(lat=25.6542, lng=-80.2380, label="Accessible Restroom 3B"),
    ],
}

# ── Language-aware greetings ─────────────────────────────────────
_LANG_PREFIX: dict[SupportedLanguage, str] = {
    SupportedLanguage.EN: "",
    SupportedLanguage.ES: "🇪🇸 ",
    SupportedLanguage.FR: "🇫🇷 ",
    SupportedLanguage.DE: "🇩🇪 ",
}


def _detect_facility(message: str) -> Optional[str]:
    """Return the first matching facility keyword, or None."""
    msg = message.lower()
    for facility in _FACILITY_COORDS:
        if facility in msg:
            return facility
    # Common aliases
    if any(w in msg for w in ("bathroom", "toilet", "washroom", "lavatory")):
        return "restroom"
    if any(w in msg for w in ("eat", "drink", "hungry", "thirsty", "snack", "beverage")):
        return "food"
    if any(w in msg for w in ("gate", "entrance", "leave", "way out")):
        return "exit"
    if any(w in msg for w in ("medical", "nurse", "doctor", "injury", "hurt")):
        return "first aid"
    if any(w in msg for w in ("shop", "store", "souvenir", "jersey", "buy")):
        return "merchandise"
    if any(w in msg for w in ("wheelchair", "disability", "mobility", "ramp", "elevator")):
        return "accessible"
    if any(w in msg for w in ("shuttle", "bus", "transport", "taxi", "uber", "ride")):
        return "parking"
    return None


def _get_sensor_context() -> str:
    """Build a context string from live sensor data for decision support."""
    try:
        crowd = generate_crowd_density()
        alerts = generate_alerts()
        crowded_zones = [z for z in crowd if z.density_pct >= 75]
        context_parts = []
        if crowded_zones:
            zones_str = ", ".join(
                f"{z.zone.value} ({z.density_pct}%)" for z in crowded_zones
            )
            context_parts.append(f"High-density zones: {zones_str}")
        if alerts:
            alert_str = "; ".join(
                f"[{a.severity}] {a.message}" for a in alerts[:3]
            )
            context_parts.append(f"Active alerts: {alert_str}")
        return "\n".join(context_parts) if context_parts else ""
    except Exception:
        return ""


def _get_role_context(role: UserRole) -> str:
    """Return role-specific system instructions."""
    role_instructions = {
        UserRole.FAN: (
            "You are speaking to a fan attending the match. "
            "Be friendly, enthusiastic, and helpful. Focus on navigation, "
            "food, facilities, and the fan experience."
        ),
        UserRole.STAFF: (
            "You are speaking to venue staff. Provide operational details, "
            "crowd management recommendations, and facility status updates. "
            "Include specific zone codes and action items."
        ),
        UserRole.VOLUNTEER: (
            "You are speaking to a volunteer helper. Provide clear directions "
            "they can relay to fans, and alert them to any current issues "
            "they should be aware of."
        ),
        UserRole.ORGANIZER: (
            "You are speaking to a tournament organizer. Provide high-level "
            "analytics, capacity metrics, sustainability KPIs, and strategic "
            "recommendations."
        ),
    }
    return role_instructions.get(role, role_instructions[UserRole.FAN])


def _build_simulated_reply(
    message: str,
    language: SupportedLanguage,
    role: UserRole = UserRole.FAN,
) -> ChatResponse:
    """Build a deterministic reply without calling the LLM."""
    prefix = _LANG_PREFIX.get(language, "")
    facility = _detect_facility(message)

    # Staff/organizer get sensor context in their response
    sensor_note = ""
    if role in (UserRole.STAFF, UserRole.ORGANIZER):
        ctx = _get_sensor_context()
        if ctx:
            sensor_note = f"\n\n📊 **Live Status:**\n{ctx}"

    if facility:
        waypoints = _FACILITY_COORDS[facility]
        route = NavigationRoute(
            waypoints=waypoints,
            eta_minutes=round(len(waypoints) * 1.2, 1),
            distance_meters=round(len(waypoints) * 45.0, 1),
        )
        reply_map = {
            SupportedLanguage.EN: f"I've plotted a route to the nearest {facility}. Follow the highlighted path on the map – estimated arrival in {route.eta_minutes} minutes.{sensor_note}",
            SupportedLanguage.ES: f"He trazado una ruta al {facility} más cercano. Sigue el camino marcado en el mapa – llegarás en {route.eta_minutes} minutos.{sensor_note}",
            SupportedLanguage.FR: f"J'ai tracé un itinéraire vers les {facility} les plus proches. Suivez le chemin surligné – arrivée estimée dans {route.eta_minutes} minutes.{sensor_note}",
            SupportedLanguage.DE: f"Ich habe eine Route zur nächsten {facility} eingezeichnet. Folgen Sie dem markierten Weg – geschätzte Ankunft in {route.eta_minutes} Minuten.{sensor_note}",
        }
        return ChatResponse(
            reply=f"{prefix}{reply_map.get(language, reply_map[SupportedLanguage.EN])}",
            language=language,
            route=route,
        )

    # General Q&A fallback
    general_map = {
        SupportedLanguage.EN: (
            "Welcome to the FIFA World Cup 2026! I'm your Smart Stadium Assistant. "
            "I can help you find restrooms, food courts, exits, first aid stations, "
            "merchandise shops, VIP lounges, and accessible facilities. I also monitor "
            "crowd density and sustainability metrics in real time. How can I assist you today?"
            f"{sensor_note}"
        ),
        SupportedLanguage.ES: (
            "¡Bienvenido al Mundial de la FIFA 2026! Soy tu Asistente Inteligente "
            "del Estadio. Puedo ayudarte a encontrar baños, zonas de comida, "
            "salidas, estaciones de primeros auxilios, tiendas de merchandising "
            "y salones VIP. ¿En qué puedo ayudarte hoy?"
            f"{sensor_note}"
        ),
        SupportedLanguage.FR: (
            "Bienvenue à la Coupe du Monde de la FIFA 2026 ! Je suis votre "
            "Assistant Intelligent du Stade. Je peux vous aider à trouver les "
            "toilettes, les espaces restauration, les sorties, les postes de "
            "premiers secours et les boutiques. Comment puis-je vous aider ?"
            f"{sensor_note}"
        ),
        SupportedLanguage.DE: (
            "Willkommen zur FIFA Fussball-Weltmeisterschaft 2026! Ich bin Ihr "
            "Intelligenter Stadion-Assistent. Ich kann Ihnen helfen, Toiletten, "
            "Essens-Bereiche, Ausgänge, Erste-Hilfe-Stationen und VIP-Lounges "
            "zu finden. Wie kann ich Ihnen helfen?"
            f"{sensor_note}"
        ),
    }
    return ChatResponse(
        reply=f"{prefix}{general_map.get(language, general_map[SupportedLanguage.EN])}",
        language=language,
    )


# ── Public API ───────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are the Smart Stadium Assistant for the FIFA World Cup 2026.
You help fans navigate the stadium, answer questions about facilities,
provide crowd-density updates, share sustainability metrics, and generate
operational alerts for staff. Always be helpful, concise, and friendly.

When a user asks for directions, include JSON waypoints in your response
using the format: {"waypoints": [{"lat": ..., "lng": ..., "label": "..."}]}

Respond in the language specified by the user.
"""


async def ask_assistant(
    message: str,
    language: SupportedLanguage = SupportedLanguage.EN,
    role: UserRole = UserRole.FAN,
    session_id: Optional[str] = None,
) -> ChatResponse:
    """Send a message to the LLM and return a structured response.

    Falls back to a deterministic simulator when no API key is configured.

    Args:
        message: The user's question or command (already sanitised).
        language: Desired response language.
        role: User persona (fan, staff, volunteer, organizer).
        session_id: Optional conversation session ID.

    Returns:
        A validated ``ChatResponse`` with the AI reply and optional route.
    """
    api_key = get_api_key()

    # Store user message in session history
    _append_history(session_id, "user", message)

    if not api_key:
        logger.info("No API key – using simulated response.")
        result = _build_simulated_reply(message, language, role)
        _append_history(session_id, "assistant", result.reply)
        return result

    # ── Real LLM call via Groq API ───────────────────────────────
    try:
        client = _get_client()
        lang_instruction = {
            SupportedLanguage.EN: "Respond in English.",
            SupportedLanguage.ES: "Responde en español.",
            SupportedLanguage.FR: "Réponds en français.",
            SupportedLanguage.DE: "Antworte auf Deutsch.",
        }

        # Build context-rich system prompt
        sensor_ctx = _get_sensor_context()
        role_ctx = _get_role_context(role)
        system = (
            f"{_SYSTEM_PROMPT}\n"
            f"{lang_instruction.get(language, '')}\n"
            f"{role_ctx}\n"
            f"{f'Current stadium status: {sensor_ctx}' if sensor_ctx else ''}"
        )

        # Build messages including system prompt
        history = _get_history(session_id)
        messages = [
            {"role": "system", "content": system}
        ] + history + [{"role": "user", "content": message}]

        payload = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 1024,
        }

        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        reply_text = data["choices"][0]["message"]["content"]

        # Extract navigation route if applicable
        route = None
        facility = _detect_facility(message)
        if facility and facility in _FACILITY_COORDS:
            waypoints = _FACILITY_COORDS[facility]
            route = NavigationRoute(
                waypoints=waypoints,
                eta_minutes=round(len(waypoints) * 1.2, 1),
                distance_meters=round(len(waypoints) * 45.0, 1),
            )

        _append_history(session_id, "assistant", reply_text)

        return ChatResponse(
            reply=reply_text,
            language=language,
            route=route,
        )

    except httpx.HTTPError:
        logger.exception("HTTP error during Groq LLM call – falling back to simulator.")
        result = _build_simulated_reply(message, language, role)
        _append_history(session_id, "assistant", result.reply)
        return result
    except Exception:
        logger.exception("Unexpected error in Groq LLM call – falling back to simulator.")
        result = _build_simulated_reply(message, language, role)
        _append_history(session_id, "assistant", result.reply)
        return result
