"""Facility and building information for The Shard reception.

get_available_facilities returns a catalog of keys and search terms so the
LLM can map natural language ("where's the loo") to a key. get_facility_info
returns directions and details for that key.
"""

from __future__ import annotations

import db


def get_available_facilities() -> str:
    """
    List available facilities for semantic search.

    Use when the visitor asks about a facility but you need to map their wording
    to the correct facility key. Returns facility keys with common search terms.
    Then call get_facility_info with the matching key.
    """
    facilities = db.get_all_facilities()
    lines = []
    for key, terms, _ in facilities:
        all_terms = [key, *terms]
        lines.append(f"{key}: {', '.join(all_terms)}")
    return "\n".join(lines)


def get_facility_info(facility_key: str) -> str:
    """
    Get information about a facility in The Shard by its canonical key.

    Call get_available_facilities first to find the correct key via semantic match,
    then pass that key here (e.g. "bathroom", "lifts", "parking", "viewing_gallery").
    """
    if not facility_key or not facility_key.strip():
        return (
            "What would you like to know about? Call get_available_facilities to see "
            "what I can help with, then get_facility_info with the matching key."
        )

    result = db.get_facility(facility_key)
    if result:
        _, info_text = result
        return info_text
    return (
        f"I'm not sure I have information about '{facility_key}'. "
        "Call get_available_facilities to see available options, then use the matching key."
    )
