"""UK public holiday lookup for The Shard reception.

Uses the Nager.Date API (no key required). Lets Emma tell visitors when
the office is closed for bank holidays.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import httpx

logger = logging.getLogger("agent")

NAGER_API = "https://date.nager.at/api/v3/PublicHolidays"


def _holidays_for_england(holidays_data: list[dict]) -> list[tuple[date, str]]:
    """Filter to holidays that apply in England (global or GB-ENG in counties)."""
    result: list[tuple[date, str]] = []
    for h in holidays_data:
        if h.get("global") or (h.get("counties") and "GB-ENG" in h["counties"]):
            result.append((date.fromisoformat(h["date"]), h["localName"]))
    return sorted(result)


def _fetch_holidays(year: int, country: str) -> list[tuple[date, str]]:
    """Fetch and filter public holidays for a year."""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{NAGER_API}/{year}/{country}")
            resp.raise_for_status()
            data = resp.json()
        return _holidays_for_england(data)
    except (httpx.HTTPError, KeyError, ValueError) as e:
        logger.warning("Holidays API request failed for %s: %s", year, e)
        return []


# Relative date phrases -> (days offset, display label, past_tense)
_RELATIVE_WHEN: dict[str, tuple[int, str, bool]] = {
    "today": (0, "Today", False),
    "tomorrow": (1, "Tomorrow", False),
    "yesterday": (-1, "Yesterday", True),
    "the day before yesterday": (-2, "The day before yesterday", True),
    "day before yesterday": (-2, "The day before yesterday", True),
    "the day after tomorrow": (2, "The day after tomorrow", False),
    "day after tomorrow": (2, "The day after tomorrow", False),
}


def _parse_when_to_date(
    when: str,
) -> tuple[date, str, bool] | None:
    """Parse when into (check_date, label, use_past_tense). Returns None if unparseable."""
    when = (when or "today").strip().lower()
    today = date.today()

    # Check relative phrases first
    if when in _RELATIVE_WHEN:
        delta, label, past = _RELATIVE_WHEN[when]
        return (today + timedelta(days=delta), label, past)

    # Try ISO date: YYYY-MM-DD
    raw = (when or "today").strip()
    try:
        check_date = date.fromisoformat(raw)
        label = check_date.strftime("%A %d %B %Y")
        past = check_date < today
        return (check_date, label, past)
    except ValueError:
        pass

    return None


def check_public_holiday(when: str = "today", country: str = "GB") -> str:
    """
    Check if a given day is a UK public holiday.

    Use when the visitor asks "Is the office open tomorrow?", "Was yesterday
    a bank holiday?", "What about the day after tomorrow?", or "Is 25 December
    a holiday?".

    Args:
        when: One of: "today", "tomorrow", "yesterday", "the day before yesterday",
            "the day after tomorrow", or a specific date as YYYY-MM-DD (e.g. "2026-12-25")
        country: ISO country code (default GB for UK)

    Returns:
        Voice-friendly message, e.g. "Tomorrow is Good Friday. The office is closed."
    """
    parsed = _parse_when_to_date(when)
    if parsed is None:
        return (
            f"I didn't understand '{when}'. Try 'today', 'tomorrow', 'yesterday', "
            "'the day before yesterday', 'the day after tomorrow', or a date like 2026-12-25."
        )
    check_date, label, use_past = parsed

    # Fetch relevant years (for dates near year boundaries)
    years = {check_date.year}
    if check_date.month == 12 and check_date.day > 25:
        years.add(check_date.year + 1)
    if check_date.month == 1 and check_date.day < 7:
        years.add(check_date.year - 1)
    holidays: list[tuple[date, str]] = []
    for year in years:
        holidays.extend(_fetch_holidays(year, country))

    holiday_map = dict(holidays)
    verb = "was" if use_past else "is"
    if check_date in holiday_map:
        name = holiday_map[check_date]
        return f"{label} {verb} {name}, a public holiday. The office is closed."
    return f"{label} {verb} a normal working day."
