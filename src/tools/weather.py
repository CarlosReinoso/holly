"""Weather lookup for The Shard reception.

Uses the Open-Meteo API (no key required). Supports UK cities via a
predefined coordinate map; other locations use the geocoding API.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("agent")

# Open-Meteo: free, no API key for non-commercial use
OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Major city coordinates for quick lookup (avoids geocoding for common queries)
CITY_COORDINATES: dict[str, tuple[float, float]] = {
    "london": (51.5074, -0.1278),
    "liverpool": (53.4084, -2.9916),
    "manchester": (53.4808, -2.2426),
    "birmingham": (52.4862, -1.8904),
    "edinburgh": (55.9533, -3.1883),
    "here": (51.5074, -0.1278),
    "the shard": (51.5045, -0.0865),
}

# WMO Weather interpretation codes (simplified for voice)
WEATHER_DESCRIPTIONS: dict[int, str] = {
    0: "clear",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "foggy",
    51: "light drizzle",
    53: "drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "slight rain showers",
    81: "rain showers",
    82: "heavy rain showers",
    95: "thunderstorms",
    96: "thunderstorms with hail",
    99: "thunderstorms with heavy hail",
}


def _get_weather_description(code: int) -> str:
    """Convert WMO weather code to a short, voice-friendly description."""
    return WEATHER_DESCRIPTIONS.get(code, "mixed conditions" if code > 0 else "clear")


def _resolve_coordinates(location: str) -> tuple[float, float] | None:
    """Resolve location to (lat, lon) via predefined city map or geocoding."""
    key = location.strip().lower()
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]
    return None


def _fetch_geocoding(name: str) -> tuple[float, float] | None:
    """Fetch coordinates from Open-Meteo geocoding API."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(
                GEOCODING_URL,
                params={"name": name, "count": 1, "language": "en"},
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if results:
                r = results[0]
                return (r["latitude"], r["longitude"])
    except (httpx.HTTPError, KeyError) as e:
        logger.warning("Geocoding failed for %s: %s", name, e)
    return None


def _fetch_weather(lat: float, lon: float) -> dict[str, Any] | None:
    """Fetch current weather from Open-Meteo."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(
                f"{OPEN_METEO_BASE}/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,weather_code",
                    "timezone": "Europe/London",
                },
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as e:
        logger.warning("Weather API request failed: %s", e)
        return None


def lookup_weather(location: str) -> str:
    """
    Look up current weather for a location.

    Uses the Open-Meteo API (free, no API key). Defaults to London if the
    location is unclear. Supports UK cities and geocoding for other places.
    """
    if not location or not location.strip():
        location = "London"

    loc = location.strip()
    coords = _resolve_coordinates(loc)

    if coords is None:
        coords = _fetch_geocoding(loc)
        if coords is None:
            return (
                f"I couldn't find weather for {loc}. "
                "I can tell you about London if you're heading outside."
            )

    data = _fetch_weather(coords[0], coords[1])
    if not data:
        return (
            "The weather service isn't responding at the moment. "
            "You might want to check your phone before heading out."
        )

    current = data.get("current", {})
    temp = current.get("temperature_2m")
    code = current.get("weather_code", 0)
    desc = _get_weather_description(int(code))

    display_location = loc if loc.lower() != "here" else "London"
    temp_str = f"{round(temp)} degrees" if temp is not None else "unknown"

    return (
        f"It's {temp_str} Celsius and {desc} in {display_location} at the moment. "
        "Might be worth grabbing a coat if you're heading out."
    )
