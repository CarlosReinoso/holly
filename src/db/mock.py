"""MockRepository: in-memory implementation with mock data."""

from __future__ import annotations

from db.repository import Repository


class MockRepository(Repository):
    """In-memory repository with mock directory and facility data."""

    def __init__(self) -> None:
        self._persons: dict[str, dict] = {
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
        self._facilities: dict[str, tuple[list[str], str]] = {
            "bathroom": (
                ["toilet", "restroom", "loo", "lavatory", "wc", "gents", "ladies"],
                "The restrooms are just past the lifts on the left-hand side. There are also facilities on every floor if you're heading up.",
            ),
            "lifts": (
                ["lift", "elevator", "elevators"],
                "The lifts are to your right as you face the reception desk. Press your floor number once you're inside. The express lifts go to the viewing gallery on the top floors.",
            ),
            "lobby": (
                ["reception area"],
                "You're in the main lobby. The seating area is behind you, and the lifts are to your right. Reception is here if you need anything else.",
            ),
            "waiting_area": (
                ["waiting", "waiting room", "seating", "lounge", "where to wait"],
                "The waiting area is the seating section behind you in the lobby. Make yourself comfortable. We'll let you know when your host can see you.",
            ),
            "cafe": (
                ["coffee", "café", "food", "light bites", "pastries"],
                "There's a cafe on the ground floor, just past the main entrance to the left.",
            ),
            "restaurant": (
                ["restaurants", "dining", "eat"],
                "Several restaurants in The Shard. The Shangri-La hotel has dining on the upper floors.",
            ),
            "water": (
                ["drinking water"],
                "Complimentary water in the lobby. Water coolers on most office floors.",
            ),
            "vending": (
                ["vending machine", "vending machines", "snacks", "drinks"],
                "Vending machines on the ground floor near the cafe.",
            ),
            "entrance": (
                ["main entrance", "exit", "exits", "way out"],
                "The main entrance is behind you. Security is at the doors.",
            ),
            "accessibility": (
                ["disabled access", "wheelchair", "accessible", "step-free"],
                "The Shard is fully accessible. Step-free access via the main entrance. Accessible restrooms on every floor.",
            ),
            "hours": (
                ["opening hours", "opening times", "reception hours", "when open"],
                "Reception 7am to 7pm on weekdays.",
            ),
            "wifi": (
                ["wi-fi", "internet", "guest wifi"],
                "Guest WiFi is Shard-Guest. Password on lobby screens or ask reception.",
            ),
            "security": ([], "Security 24 hours. Main desk near the entrance."),
            "emergency": (
                ["fire exit", "fire exits", "evacuation"],
                "Follow signs to nearest fire exit. Assembly point south side. Use stairwells, not lifts.",
            ),
            "first_aid": (
                ["first aid", "medical", "ambulance"],
                "First aid at reception. Tell any staff or security for help.",
            ),
            "parking": (
                ["car park", "car parking", "where to park"],
                "No public parking. Nearest car parks at The Shard's base. London Bridge station nearby.",
            ),
            "bike_storage": (
                ["bicycle", "bike", "cycling"],
                "Secure bicycle storage in the basement. Ask reception for access.",
            ),
            "taxi": (
                ["taxis", "uber", "ride", "ride-hail"],
                "Taxi rank on St Thomas Street, outside main entrance.",
            ),
            "transport": (
                ["tube", "train", "london bridge", "bus", "how to get here"],
                "London Bridge station two-minute walk. Jubilee and Northern lines.",
            ),
            "luggage": (
                ["coat check", "coat storage", "bag storage", "bags", "coats"],
                "Bags and coats at reception.",
            ),
            "lockers": (
                [],
                "Lockers in basement for tenants. Visitors can leave bags at reception.",
            ),
            "atm": (
                ["cash machine", "cash"],
                "Cash machine in ground floor retail area.",
            ),
            "post": (
                ["mail", "deliveries"],
                "Post and deliveries to mail room. Show ID to drop off.",
            ),
            "printing": (
                ["photocopying", "photocopy", "print"],
                "No public printing. Your host can arrange it.",
            ),
            "meeting_rooms": (
                ["meeting room", "conference room"],
                "Meeting rooms bookable through your host's organisation.",
            ),
            "viewing_gallery": (
                ["viewing", "view", "observation deck", "sky deck", "the view"],
                "The View from The Shard is on levels 68, 69, 72. Dedicated lifts to the left of the lobby. Tickets at counter or online.",
            ),
            "hotel": (
                ["shangri-la", "accommodation"],
                "Shangri-La Hotel floors 34-52. Dedicated lifts for hotel guests.",
            ),
            "charging": (
                ["phone charging", "charging station", "charge phone", "usb"],
                "Phone charging in lobby and near cafe.",
            ),
            "smoking": (
                ["smoking area"],
                "Smoke-free indoors. Smoking area outside, right as you exit.",
            ),
            "baby_changing": (
                ["nursery", "nappy", "nappies"],
                "Baby changing in accessible restrooms on ground floor.",
            ),
            "lost_found": (
                ["lost property", "lost and found"],
                "Lost property at reception.",
            ),
            "prayer_room": (
                ["quiet room", "multi-faith"],
                "Multi-faith quiet room on lower ground floor. Ask reception.",
            ),
        }

    def search_persons(self, query: str) -> list[tuple[str, dict]]:
        if not query or not query.strip():
            return []
        words = [w.lower().strip() for w in query.split() if w.strip()]
        if not words:
            return []
        return [
            (n, d)
            for n, d in self._persons.items()
            if all(w in n.lower() for w in words)
        ]

    def search_persons_by_context(self, query: str) -> list[tuple[str, dict]]:
        if not query or not query.strip():
            return []
        words = [w.lower().strip() for w in query.split() if w.strip()]
        if not words:
            return []
        return [
            (n, d)
            for n, d in self._persons.items()
            if all(w in f"{n.lower()} {d['company'].lower()}" for w in words)
        ]

    def get_person(self, name: str) -> tuple[str, dict] | None:
        if not name or not name.strip():
            return None
        key = next(
            (k for k in self._persons if k.lower() == name.strip().lower()), None
        )
        return (key, self._persons[key]) if key else None

    def get_all_facilities(self) -> list[tuple[str, list[str], str]]:
        return [(k, list(t), info) for k, (t, info) in self._facilities.items()]

    def get_facility(self, key: str) -> tuple[list[str], str] | None:
        if not key or not key.strip():
            return None
        k = key.strip().lower().replace(" ", "_")
        return self._facilities.get(k)
