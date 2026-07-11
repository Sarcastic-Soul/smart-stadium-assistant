"""Sensor data simulators – generate realistic stadium telemetry.

All data is procedurally generated using deterministic seeds mixed with
controlled randomness to produce plausible readings that vary over time.
"""

from __future__ import annotations

import math
import random
import uuid
from datetime import UTC, datetime

from app.schemas import (
    CrowdDensity,
    OperationalAlert,
    SustainabilityMetrics,
    ZoneId,
)

# ── Zone capacity (max headcount) ────────────────────────────────
_ZONE_CAPACITY: dict[ZoneId, int] = {
    ZoneId.NORTH_STAND: 15000,
    ZoneId.SOUTH_STAND: 15000,
    ZoneId.EAST_STAND: 12000,
    ZoneId.WEST_STAND: 12000,
    ZoneId.CONCOURSE_A: 5000,
    ZoneId.CONCOURSE_B: 5000,
    ZoneId.VIP_LOUNGE: 800,
    ZoneId.FIELD_LEVEL: 200,
    ZoneId.PARKING_A: 3000,
    ZoneId.PARKING_B: 3000,
}

# ── AI-generated recommendations per density band ───────────────
_RECOMMENDATIONS: dict[str, str] = {
    "low": "This area is uncrowded – great time to visit!",
    "moderate": "Moderate crowd levels. Normal wait times expected.",
    "high": "High density detected. Consider alternative routes.",
    "critical": "⚠️ Near capacity! Staff should redirect foot traffic immediately.",
}


def _time_factor() -> float:
    """Return a 0-1 factor based on the current minute to simulate ebb & flow."""
    now = datetime.now(UTC)
    minute = now.minute + now.second / 60
    return (math.sin(minute * math.pi / 30) + 1) / 2  # 0→1 over 30 min


def generate_crowd_density() -> list[CrowdDensity]:
    """Generate crowd-density readings for every stadium zone.

    Density varies sinusoidally over time with added noise to feel realistic.
    """
    factor = _time_factor()
    results: list[CrowdDensity] = []

    for zone, capacity in _ZONE_CAPACITY.items():
        base_pct = random.uniform(30, 90) * factor + random.uniform(5, 15)
        density_pct = min(100.0, round(base_pct, 1))
        headcount = int(capacity * density_pct / 100)

        if density_pct < 40:
            rec = _RECOMMENDATIONS["low"]
        elif density_pct < 65:
            rec = _RECOMMENDATIONS["moderate"]
        elif density_pct < 85:
            rec = _RECOMMENDATIONS["high"]
        else:
            rec = _RECOMMENDATIONS["critical"]

        results.append(
            CrowdDensity(
                zone=zone,
                density_pct=density_pct,
                headcount=headcount,
                recommendation=rec,
            )
        )

    return results


def generate_sustainability() -> SustainabilityMetrics:
    """Generate realistic sustainability metrics for the stadium.

    Values are based on a 60 000-seat venue during a match day.
    """
    factor = _time_factor()
    base_energy = 2400.0 + factor * 1200.0

    return SustainabilityMetrics(
        energy_kwh=round(base_energy + random.uniform(-100, 100), 1),
        solar_generation_kwh=round(
            800.0 * factor + random.uniform(0, 200), 1
        ),
        water_liters=round(
            18000.0 + factor * 7000 + random.uniform(-500, 500), 1
        ),
        waste_kg=round(3200.0 + factor * 1800 + random.uniform(-200, 200), 1),
        recycling_rate_pct=round(random.uniform(58, 78), 1),
        carbon_offset_kg=round(
            1200.0 + factor * 600 + random.uniform(-50, 50), 1
        ),
    )


# ── Alert templates ──────────────────────────────────────────────
_ALERT_TEMPLATES: list[dict[str, str]] = [
    {
        "severity": "critical",
        "zone": ZoneId.CONCOURSE_A.value,
        "message": "Restroom 12 overflow detected – dispatch cleaning crew immediately.",
    },
    {
        "severity": "warning",
        "zone": ZoneId.NORTH_STAND.value,
        "message": "Crowd density in Section 114 approaching 95 %. Open auxiliary gate N3.",
    },
    {
        "severity": "info",
        "zone": ZoneId.PARKING_A.value,
        "message": "Parking Lot A is 88 % full. Begin directing traffic to Lot B.",
    },
    {
        "severity": "warning",
        "zone": ZoneId.EAST_STAND.value,
        "message": "Ambient temperature sensor E7 reading 38 °C – activate misting fans.",
    },
    {
        "severity": "critical",
        "zone": ZoneId.VIP_LOUNGE.value,
        "message": "HVAC unit VIP-2 offline. Maintenance dispatched – ETA 12 min.",
    },
    {
        "severity": "info",
        "zone": ZoneId.FIELD_LEVEL.value,
        "message": "Pitch irrigation cycle complete. Sprinklers deactivated.",
    },
    {
        "severity": "warning",
        "zone": ZoneId.CONCOURSE_B.value,
        "message": "Point-of-sale terminal CB-09 unresponsive. IT team notified.",
    },
    {
        "severity": "info",
        "zone": ZoneId.SOUTH_STAND.value,
        "message": "Accessibility ramp S2 inspection passed. All clear.",
    },
]


def generate_alerts() -> list[OperationalAlert]:
    """Return a subset of operational alerts (simulated).

    Randomly selects 2-4 alerts from the template pool to keep the
    dashboard dynamic.
    """
    count = random.randint(2, 4)
    selected = random.sample(_ALERT_TEMPLATES, k=min(count, len(_ALERT_TEMPLATES)))

    return [
        OperationalAlert(
            alert_id=str(uuid.uuid4())[:8],
            severity=tpl["severity"],
            zone=ZoneId(tpl["zone"]),
            message=tpl["message"],
        )
        for tpl in selected
    ]
