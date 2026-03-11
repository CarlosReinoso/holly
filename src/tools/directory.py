"""Person directory lookup for The Shard reception."""

from __future__ import annotations

# Mock person directory - in production this would be a database or directory service
# Room numbers use hotel standard: floor + 2-digit room (e.g. 1801 = Floor 18, Room 01)
PERSON_DIRECTORY: dict[str, dict] = {
    "Sarah Thompson": {
        "floor": 18,
        "room": "1801",
        "company": "Acme Finance",
        "status": "available",
    },
    "Michael Carter": {
        "floor": 21,
        "room": "2103",
        "company": "Carter Legal",
        "status": "in_meeting",
        "meeting_eta_minutes": 15,
    },
    "Emma Davis": {
        "floor": 12,
        "room": "1205",
        "company": "Davis Marketing",
        "status": "away",
        "return_time": "afternoon",
    },
    "James Wilson": {
        "floor": 24,
        "room": "2401",
        "company": "Wilson Tech",
        "status": "available",
    },
    "Sophie Brown": {
        "floor": 15,
        "room": "1512",
        "company": "Brown HR",
        "status": "in_meeting",
        "meeting_eta_minutes": 5,
    },
    "David Chen": {
        "floor": 19,
        "room": "1908",
        "company": "Acme Finance",
        "status": "available",
    },
    "Olivia Martinez": {
        "floor": 22,
        "room": "2211",
        "company": "Carter Legal",
        "status": "away",
        "return_time": "tomorrow",
    },
    "John Smith": {
        "floor": 14,
        "room": "1402",
        "company": "Smith Engineering",
        "status": "available",
    },
    "John Williams": {
        "floor": 20,
        "room": "2007",
        "company": "Acme Finance",
        "status": "available",
    },
    "Rachel Green": {
        "floor": 16,
        "room": "1604",
        "company": "Green Associates",
        "status": "out_to_lunch",
        "return_time": "1pm",
    },
    "Tom Bradley": {
        "floor": 23,
        "room": "2309",
        "company": "Bradley Consulting",
        "status": "on_phone",
        "call_eta_minutes": 10,
    },
    "Lisa Park": {
        "floor": 17,
        "room": "1702",
        "company": "Park Design",
        "status": "do_not_disturb",
    },
    "Alex Kumar": {
        "floor": 19,
        "room": "1915",
        "company": "Wilson Tech",
        "status": "in_transit",
        "arrival_eta_minutes": 15,
    },
}


def _normalize_name(name: str) -> str:
    """Normalize name for fuzzy matching (strip, title case)."""
    return " ".join(word.strip().capitalize() for word in name.split() if word.strip())


def _search_persons(query: str) -> list[tuple[str, dict]]:
    """Find persons by partial/semantic name match.

    Matches when all query words appear in the person's name (case-insensitive).
    """
    if not query or not query.strip():
        return []
    words = [w.lower().strip() for w in query.split() if w.strip()]
    if not words:
        return []
    matches: list[tuple[str, dict]] = []
    for name, data in PERSON_DIRECTORY.items():
        if all(word in name.lower() for word in words):
            matches.append((name, data))
    return matches


def _search_persons_by_context(query: str) -> list[tuple[str, dict]]:
    """Find persons by name or company context.

    Matches when all query words appear in the person's name OR company.
    E.g. "John Smith Engineering" matches "John Smith" (Smith Engineering).
    """
    if not query or not query.strip():
        return []
    words = [w.lower().strip() for w in query.split() if w.strip()]
    if not words:
        return []
    matches: list[tuple[str, dict]] = []
    for name, data in PERSON_DIRECTORY.items():
        searchable = f"{name.lower()} {data['company'].lower()}"
        if all(word in searchable for word in words):
            matches.append((name, data))
    return matches


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

    matches = _search_persons_by_context(query)
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

    matches = _search_persons(name)
    if not matches:
        return f"I'm sorry, I couldn't find anyone named {_normalize_name(name)} in our directory. They may work in a different building, or you might have the spelling slightly wrong. Would you like to try again or leave a message?"

    if len(matches) > 1:
        lines = [
            f"I found {len(matches)} people with that name:",
            *(
                f"- {name} ({data['company']} – Floor {data['floor']}, Room {data['room']})"
                for name, data in matches
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
