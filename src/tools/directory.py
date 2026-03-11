"""Person directory lookup for The Shard reception."""

from __future__ import annotations

import db


def _normalize_name(name: str) -> str:
    """Normalize name for fuzzy matching (strip, title case)."""
    return " ".join(word.strip().capitalize() for word in name.split() if word.strip())


def search_persons_for_lookup(query: str) -> str:
    """
    Search persons by name and/or company for semantic lookup.

    Use when the visitor gives a partial name or context like "John from Smith Engineering".
    Returns full names and companies so you can resolve to the correct person, then
    call lookup_person with the full name.

    Args:
        query: Partial name and/or company (e.g. "John", "John Smith Engineering", "Sarah Acme")

    Returns:
        Formatted list of matches: "Full Name (Company)" per line, or a no-match message.
    """
    if not query or not query.strip():
        return "I didn't catch that. Who would you like to visit? You can give a name, or a name and company."

    matches = db.search_persons_by_context(query)
    if not matches:
        return f"I couldn't find anyone matching '{query.strip()}'. Try the full name or a different spelling."

    lines = [f"{name} ({data['company']})" for name, data in matches]
    return "\n".join(lines)


def lookup_person(name: str) -> str:
    """
    Look up a person in The Shard directory.

    Supports partial name search. When multiple people match, returns a disambiguation message.

    Returns floor, room, company, and availability status.
    Statuses: available, in_meeting, away, out_to_lunch, on_phone, do_not_disturb, in_transit.
    """
    if not name or not name.strip():
        return "I didn't catch the name. Who would you like to visit?"

    matches = db.search_persons(name)
    if not matches:
        return (
            f"I'm sorry, I couldn't find anyone named {_normalize_name(name)} in our directory. "
            "They may work in a different building, or you might have the spelling slightly wrong. "
            "Would you like to try again or leave a message?"
        )

    if len(matches) > 1:
        lines = [
            f"I found {len(matches)} people with that name:",
            *(
                f"- {n} ({d['company']} - Floor {d['floor']}, Room {d['room']})"
                for n, d in matches
            ),
            "Which one are you visiting?",
        ]
        return "\n".join(lines)

    found_name, person = matches[0]
    status = person["status"]
    floor = person["floor"]
    room = person["room"]
    company = person["company"]

    if status == "available":
        return (
            f"{found_name} is in Room {room} on Floor {floor}, {company}. "
            "They're available to see you now. The lifts are to your right."
        )
    if status == "in_meeting":
        eta = person.get("meeting_eta_minutes")
        eta_str = f"about {eta} minutes" if eta else "a short while"
        return (
            f"{found_name} is in Room {room} on Floor {floor}, {company}, "
            f"but they're currently in a meeting. They should be free in {eta_str}. "
            "Would you like to take a seat in the lobby? I can have someone notify you when they're ready."
        )
    if status == "away":
        return_time = person.get("return_time", "later")
        return (
            f"I'm afraid {found_name} isn't in the building at the moment. "
            f"They're expected back {return_time}. "
            "Would you like me to leave a message or help you reschedule your visit?"
        )
    if status == "out_to_lunch":
        return_time = person.get("return_time", "soon")
        return (
            f"{found_name} is in Room {room} on Floor {floor}, {company}, "
            f"but they're out to lunch. They should be back {return_time}. "
            "Would you like to wait in the lobby or leave a message?"
        )
    if status == "on_phone":
        eta = person.get("call_eta_minutes")
        eta_str = f"about {eta} minutes" if eta else "a short while"
        return (
            f"{found_name} is in Room {room} on Floor {floor}, {company}, "
            f"but they're on a call at the moment. They should be free in {eta_str}. "
            "Would you like to take a seat and we'll let them know you're here?"
        )
    if status == "do_not_disturb":
        return (
            f"{found_name} is in Room {room} on Floor {floor}, {company}, "
            "but they've asked not to be disturbed. Would you like to leave a message or schedule a different time?"
        )
    if status == "in_transit":
        eta = person.get("arrival_eta_minutes")
        eta_str = f"in about {eta} minutes" if eta else "shortly"
        return (
            f"{found_name} is on their way to the building and should arrive {eta_str}. "
            f"Room {room} on Floor {floor}, {company}. "
            "Would you like to take a seat in the lobby until they arrive?"
        )

    return f"{found_name} is in Room {room} on Floor {floor}, {company}."
