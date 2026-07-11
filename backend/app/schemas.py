"""Pydantic schemas for request / response validation.

Every public endpoint uses strict Pydantic models so that invalid payloads
are rejected before they reach any business logic.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Chat ─────────────────────────────────────────────────────────

class SupportedLanguage(str, Enum):
    """ISO-639-1 codes supported by the assistant."""

    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"


class UserRole(str, Enum):
    """User persona – controls response detail level and capabilities."""

    FAN = "fan"
    STAFF = "staff"
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"


class ChatRequest(BaseModel):
    """Incoming chat message from a fan or staff member."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question or command.",
    )
    language: SupportedLanguage = Field(
        default=SupportedLanguage.EN,
        description="Preferred response language (auto-detected if omitted).",
    )
    role: UserRole = Field(
        default=UserRole.FAN,
        description="User persona – fan, staff, volunteer, or organizer.",
    )
    session_id: Optional[str] = Field(
        default=None,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Optional session identifier (alphanumeric, hyphens, underscores).",
    )

    @field_validator("message")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Remove leading/trailing whitespace from the message."""
        return value.strip()


class Waypoint(BaseModel):
    """A single coordinate on a navigation route."""

    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    label: Optional[str] = None


class NavigationRoute(BaseModel):
    """Turn-by-turn route with estimated time of arrival."""

    waypoints: list[Waypoint] = []
    eta_minutes: Optional[float] = None
    distance_meters: Optional[float] = None


class ChatResponse(BaseModel):
    """AI-generated response to the user."""

    reply: str
    language: SupportedLanguage
    route: Optional[NavigationRoute] = None
    alert: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── Sensors ──────────────────────────────────────────────────────

class ZoneId(str, Enum):
    """Logical zones inside the stadium."""

    NORTH_STAND = "north_stand"
    SOUTH_STAND = "south_stand"
    EAST_STAND = "east_stand"
    WEST_STAND = "west_stand"
    CONCOURSE_A = "concourse_a"
    CONCOURSE_B = "concourse_b"
    VIP_LOUNGE = "vip_lounge"
    FIELD_LEVEL = "field_level"
    PARKING_A = "parking_a"
    PARKING_B = "parking_b"


class CrowdDensity(BaseModel):
    """Crowd-density reading for a single zone."""

    zone: ZoneId
    density_pct: float = Field(..., ge=0, le=100, description="Occupancy percentage.")
    headcount: int = Field(..., ge=0)
    recommendation: Optional[str] = None


class SustainabilityMetrics(BaseModel):
    """Real-time energy and waste metrics."""

    energy_kwh: float = Field(..., ge=0)
    solar_generation_kwh: float = Field(..., ge=0)
    water_liters: float = Field(..., ge=0)
    waste_kg: float = Field(..., ge=0)
    recycling_rate_pct: float = Field(..., ge=0, le=100)
    carbon_offset_kg: float = Field(..., ge=0)


class OperationalAlert(BaseModel):
    """Staff-facing alert for facility issues."""

    alert_id: str
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    zone: ZoneId
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    acknowledged: bool = False


class SensorSnapshot(BaseModel):
    """Complete telemetry snapshot returned by /sensors/snapshot."""

    crowd: list[CrowdDensity]
    sustainability: SustainabilityMetrics
    alerts: list[OperationalAlert]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
