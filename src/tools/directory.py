"""Employee directory lookup for The Shard reception."""

from __future__ import annotations

# Mock employee directory - in production this would be a database or directory service
EMPLOYEE_DIRECTORY: dict[str, dict] = {
    "Sarah Thompson": {
        "floor": 18,
        "department": "Finance",
        "status": "available",
        "notes": "Head of Finance",
    },
    "Michael Carter": {
        "floor": 21,
        "department": "Legal",
        "status": "in_meeting",
        "meeting_eta_minutes": 15,
        "notes": "Senior Counsel",
    },
    "Emma Davis": {
        "floor": 12,
        "department": "Marketing",
        "status": "away",
        "return_time": "afternoon",
        "notes": "Marketing Director",
    },
    "James Wilson": {
        "floor": 24,
        "department": "Technology",
        "status": "available",
        "notes": "CTO",
    },
    "Sophie Brown": {
        "floor": 15,
        "department": "Human Resources",
        "status": "in_meeting",
        "meeting_eta_minutes": 5,
        "notes": "HR Director",
    },
    "David Chen": {
        "floor": 19,
        "department": "Finance",
        "status": "available",
        "notes": "Financial Analyst",
    },
    "Olivia Martinez": {
        "floor": 22,
        "department": "Legal",
        "status": "away",
        "return_time": "tomorrow",
        "notes": "Associate",
    },
    "John Smith": {
        "floor": 14,
        "department": "Engineering",
        "status": "available",
        "notes": "Software Engineer",
    },
    "John Williams": {
        "floor": 20,
        "department": "Finance",
        "status": "available",
        "notes": "Accountant",
    },
}


def _normalize_name(name: str) -> str:
    """Normalize name for fuzzy matching (strip, title case)."""
    return " ".join(word.strip().capitalize() for word in name.split() if word.strip())


def _search_employees(query: str) -> list[tuple[str, dict]]:
    """Find employees by partial/semantic name match.

    Matches when all query words appear in the employee's name (case-insensitive).
    E.g. "John" matches "John Smith" and "John Williams"; "Smith" matches "John Smith".
    """
    if not query or not query.strip():
        return []
    words = [w.lower().strip() for w in query.split() if w.strip()]
    if not words:
        return []
    matches: list[tuple[str, dict]] = []
    for emp_name, emp_data in EMPLOYEE_DIRECTORY.items():
        emp_lower = emp_name.lower()
        # All query words must appear in the employee name
        if all(word in emp_lower for word in words):
            matches.append((emp_name, emp_data))
    return matches


def _search_employees_by_context(query: str) -> list[tuple[str, dict]]:
    """Find employees by name or department context.

    Matches when all query words appear in the employee's name OR department.
    E.g. "John Engineering" matches "John Smith" (Engineering).
    """
    if not query or not query.strip():
        return []
    words = [w.lower().strip() for w in query.split() if w.strip()]
    if not words:
        return []
    matches: list[tuple[str, dict]] = []
    for emp_name, emp_data in EMPLOYEE_DIRECTORY.items():
        searchable = f"{emp_name.lower()} {emp_data['department'].lower()}"
        if all(word in searchable for word in words):
            matches.append((emp_name, emp_data))
    return matches


def search_employees_for_lookup(query: str) -> str:
    """
    Search employees by name and/or department for semantic lookup.

    Use when the visitor gives a partial name or context like "John from Engineering".
    Returns full names and departments so you can resolve to the correct person, then
    call lookup_employee with the full name.

    Args:
        query: Partial name and/or department (e.g. "John", "John Engineering", "Sarah Finance")

    Returns:
        Formatted list of matches: "Full Name (Department)" per line, or a no-match message.
    """
    if not query or not query.strip():
        return "I didn't catch that. Who would you like to visit? You can give a name, or a name and department."

    matches = _search_employees_by_context(query)
    if not matches:
        return f"I couldn't find anyone matching '{query.strip()}'. Try the full name or a different spelling."

    lines = [f"{emp_name} ({emp_data['department']})" for emp_name, emp_data in matches]
    return "\n".join(lines)


def lookup_employee(name: str) -> str:
    """
    Look up an employee in The Shard directory.

    Supports partial name search (e.g. first name only, last name, or full name).
    When multiple people match, returns a disambiguation message so the visitor
    can choose by department or job.

    Returns a human-readable string with floor, department, and availability status.
    Handles: available, in_meeting, and away statuses.
    """
    if not name or not name.strip():
        return "I didn't catch the name. Who would you like to visit?"

    matches = _search_employees(name)
    if not matches:
        return f"I'm sorry, I couldn't find anyone named {_normalize_name(name)} in our directory. They may work in a different building, or you might have the spelling slightly wrong. Would you like to try again or leave a message?"

    if len(matches) > 1:
        lines = [
            f"I found {len(matches)} people with that name:",
            *(
                f"- {emp_name} ({emp_data['department']} – Floor {emp_data['floor']})"
                for emp_name, emp_data in matches
            ),
            "Which one are you visiting?",
        ]
        return "\n".join(lines)

    found_name, employee = matches[0]
    status = employee["status"]
    floor = employee["floor"]
    department = employee["department"]

    if status == "available":
        return (
            f"{found_name} is on Floor {floor} in the {department} department. "
            "They're available to see you now. The lifts are to your right."
        )
    if status == "in_meeting":
        eta = employee.get("meeting_eta_minutes")
        eta_str = f"about {eta} minutes" if eta else "a short while"
        return (
            f"{found_name} is on Floor {floor} in {department}, "
            f"but they're currently in a meeting. They should be free in {eta_str}. "
            "Would you like to take a seat in the lobby? I can have someone notify you when they're ready."
        )
    if status == "away":
        return_time = employee.get("return_time", "later")
        return (
            f"I'm afraid {found_name} isn't in the office at the moment. "
            f"They're expected back {return_time}. "
            "Would you like me to leave a message or help you reschedule your visit?"
        )

    return f"{found_name} is on Floor {floor} in {department}."
