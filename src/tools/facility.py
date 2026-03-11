"""Facility and building information for The Shard reception."""

from __future__ import annotations

# Facility key -> (search terms for LLM semantic matching, info text)
# LLM uses get_available_facilities() to match user intent, then calls get_facility_info(key)
FACILITY_CATALOG: dict[str, tuple[list[str], str]] = {
    "bathroom": (
        ["toilet", "restroom", "loo", "lavatory", "wc", "gents", "ladies"],
        "The restrooms are just past the lifts on the left-hand side. "
        "There are also facilities on every floor if you're heading up.",
    ),
    "lifts": (
        ["lift", "elevator", "elevators"],
        "The lifts are to your right as you face the reception desk. "
        "Press your floor number once you're inside. "
        "The express lifts go to the viewing gallery on the top floors.",
    ),
    "lobby": (
        ["reception area"],
        "You're in the main lobby. The seating area is behind you, "
        "and the lifts are to your right. Reception is here if you need anything else.",
    ),
    "waiting_area": (
        ["waiting", "waiting room", "seating", "lounge", "where to wait"],
        "The waiting area is the seating section behind you in the lobby. "
        "Make yourself comfortable—there's complimentary water. We'll let you know when your host can see you.",
    ),
    "cafe": (
        ["coffee", "café", "food", "light bites", "pastries"],
        "There's a cafe on the ground floor, just past the main entrance to the left. "
        "They do excellent coffee, pastries, and light bites.",
    ),
    "restaurant": (
        ["restaurants", "dining", "eat"],
        "There are several restaurants in The Shard. On the lower floors you'll find casual dining, "
        "and the viewing level has a restaurant. The Shangri-La hotel also has dining on the upper floors.",
    ),
    "water": (
        ["drinking water"],
        "Complimentary water is available in the lobby waiting area, and there are water coolers on most office floors. "
        "The cafe can also provide water if you're purchasing something.",
    ),
    "vending": (
        ["vending machine", "vending machines", "snacks", "drinks"],
        "Vending machines with snacks and drinks are on the ground floor near the cafe, "
        "and on selected office floors.",
    ),
    "entrance": (
        ["main entrance", "exit", "exits", "way out"],
        "The main entrance is behind you. Security is at the doors. "
        "If you need to step out, your host can arrange re-entry.",
    ),
    "accessibility": (
        ["disabled access", "wheelchair", "accessible", "step-free"],
        "The Shard is fully accessible. Step-free access is via the main entrance. "
        "Accessible restrooms are on the ground floor and on every floor. "
        "The lifts serve all floors. If you need assistance, please ask at reception.",
    ),
    "hours": (
        ["opening hours", "opening times", "reception hours", "when open"],
        "Reception is staffed from 7am to 7pm on weekdays. "
        "Outside those hours, you'll need to contact your host directly to arrange access.",
    ),
    "wifi": (
        ["wi-fi", "internet", "guest wifi"],
        "The guest WiFi network is Shard-Guest. The password is displayed on the screens in the lobby, "
        "or ask at reception and we can give it to you.",
    ),
    "security": (
        [],
        "Security is available 24 hours. The main desk is near the entrance. "
        "If you need assistance, just ask at reception.",
    ),
    "emergency": (
        ["fire exit", "fire exits", "evacuation"],
        "In an emergency, follow the signs to the nearest fire exit. "
        "The assembly point is on the south side of the building. "
        "Lifts should not be used in a fire—use the stairwells.",
    ),
    "first_aid": (
        ["first aid", "medical", "ambulance"],
        "First aid is available at reception. If you need immediate help, tell any member of staff "
        "or approach the security desk. They can also call for an ambulance if needed.",
    ),
    "parking": (
        ["car park", "car parking", "where to park"],
        "There's no public parking inside The Shard. The nearest car parks are at The Shard's base "
        "and in the area—we can provide directions. Many visitors use London Bridge station and walk.",
    ),
    "bike_storage": (
        ["bicycle", "bike", "cycling"],
        "There's a secure bicycle storage area in the basement. "
        "Ask at reception and we'll arrange access for you.",
    ),
    "taxi": (
        ["taxis", "uber", "ride", "ride-hail"],
        "The taxi rank is on St Thomas Street, just outside the main entrance. "
        "You can also book Uber or other ride-hail apps—the pickup point is the same.",
    ),
    "transport": (
        ["tube", "train", "london bridge", "bus", "how to get here"],
        "London Bridge station is a two-minute walk—turn left out of the main entrance. "
        "Jubilee and Northern lines plus national rail. Many buses stop nearby on London Bridge.",
    ),
    "luggage": (
        ["coat check", "coat storage", "bag storage", "bags", "coats"],
        "We can store bags and coats at reception. Larger items may need to go to the luggage storage "
        "near the entrance—ask us and we'll show you.",
    ),
    "lockers": (
        [],
        "There are lockers in the basement for tenants. Visitors can leave bags at reception—we'll keep them secure.",
    ),
    "atm": (
        ["cash machine", "cash"],
        "There's a cash machine in the ground floor retail area, past the cafe. "
        "The nearest bank is a short walk on Borough High Street.",
    ),
    "post": (
        ["mail", "deliveries"],
        "Post and deliveries for building tenants go to the mail room. "
        "If you're dropping something off, we can direct you—you'll need to show ID.",
    ),
    "printing": (
        ["photocopying", "photocopy", "print"],
        "There are no public printing facilities. If you need something printed, "
        "your host can arrange it through their office, or we can suggest a nearby print shop.",
    ),
    "meeting_rooms": (
        ["meeting room", "conference room"],
        "Meeting rooms are bookable through your host's organisation. "
        "We can direct you to the right floor once you have a room number or host name.",
    ),
    "viewing_gallery": (
        ["viewing", "view", "observation deck", "sky deck", "the view"],
        "The View from The Shard is on levels 68, 69, and 72. Access is via the dedicated lifts "
        "to the left of the main lobby. Tickets are available at the counter or online.",
    ),
    "hotel": (
        ["shangri-la", "accommodation"],
        "The Shangri-La Hotel is located in The Shard from floors 34 to 52. "
        "Hotel guests use the dedicated lifts—we can point you to the right desk.",
    ),
    "charging": (
        ["phone charging", "charging station", "charge phone", "usb"],
        "Phone charging points are in the lobby seating area and near the cafe. "
        "USB and standard sockets are available.",
    ),
    "smoking": (
        ["smoking area"],
        "The Shard is smoke-free indoors. The designated smoking area is outside the main entrance, "
        "to the right as you exit.",
    ),
    "baby_changing": (
        ["nursery", "nappy", "nappies"],
        "Baby changing facilities are in the accessible restrooms on the ground floor, "
        "and in the family restroom near the viewing gallery entrance.",
    ),
    "lost_found": (
        ["lost property", "lost and found"],
        "Lost property is held at reception. If you've lost something, describe it and we'll check. "
        "Found items can be handed in here.",
    ),
    "prayer_room": (
        ["quiet room", "multi-faith"],
        "There's a multi-faith quiet room on the lower ground floor. "
        "Ask at reception and we'll direct you.",
    ),
}


def get_available_facilities() -> str:
    """
    List available facilities for semantic search.

    Use when the visitor asks about a facility but you need to map their wording
    to the correct facility key. Returns facility keys with common search terms.
    Then call get_facility_info with the matching key.
    """
    lines = []
    for key, (terms, _) in FACILITY_CATALOG.items():
        all_terms = [key] + terms
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

    key = facility_key.strip().lower().replace(" ", "_")
    if key in FACILITY_CATALOG:
        return FACILITY_CATALOG[key][1]
    return (
        f"I'm not sure I have information about '{facility_key}'. "
        "Call get_available_facilities to see available options, then use the matching key."
    )
