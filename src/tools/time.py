"""Current time lookup for The Shard reception.

Uses the World Time API (no key required). Lets Emma give visitors the
current time for context, e.g. when someone is in a meeting and due out soon.
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

logger = logging.getLogger("agent")

WORLD_TIME_API = "https://worldtimeapi.org/api/timezone"

# Common timezones for The Shard (London) and nearby
DEFAULT_TIMEZONE = "Europe/London"


def _format_time_for_voice(dt: datetime) -> str:
    """Format datetime as natural speech: '3:10 PM' or '12:05 PM'."""
    hour = dt.hour
    minute = dt.minute
    if hour == 0:
        period = "AM"
        hour12 = 12
    elif hour < 12:
        period = "AM"
        hour12 = hour
    elif hour == 12:
        period = "PM"
        hour12 = 12
    else:
        period = "PM"
        hour12 = hour - 12
    minute_str = f"{minute:02d}" if minute else "00"
    return f"{hour12}:{minute_str} {period}"


def get_current_time(timezone: str = DEFAULT_TIMEZONE) -> str:
    """
    Get the current time for a timezone.

    Use when the visitor asks "What time is it?" or when giving context
    about meetings (e.g. "It's 3:10 PM — he should be free around 3:30").
    Defaults to Europe/London for The Shard.

    Args:
        timezone: IANA timezone (e.g. "Europe/London", "Europe/Dublin")

    Returns:
        Voice-friendly string like "It's currently 3:10 PM."
    """
    if not timezone or not timezone.strip():
        timezone = DEFAULT_TIMEZONE
    tz = timezone.strip()

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{WORLD_TIME_API}/{tz}")
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        logger.warning("World Time API request failed: %s", e)
        # Fallback to local time if API fails
        from zoneinfo import ZoneInfo

        try:
            dt = datetime.now(ZoneInfo(tz))
        except Exception:
            dt = datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
        time_str = _format_time_for_voice(dt)
        return f"It's currently {time_str}."
    except Exception as e:
        logger.warning("Time lookup failed: %s", e)
        return "I'm not sure of the exact time at the moment. You can check the lobby clocks."

    datetime_str = data.get("datetime")
    if not datetime_str:
        return "I couldn't get the current time right now."

    # Parse ISO format: 2026-03-11T15:10:00.123456+00:00
    try:
        dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return "I couldn't get the current time right now."

    time_str = _format_time_for_voice(dt)
    return f"It's currently {time_str}."
