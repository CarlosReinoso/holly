"""Repository layer for directory and facility data.

Abstract interface so we can swap MockRepository for a real DB or API
without changing the tools that depend on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Repository(ABC):
    """Abstract repository. Subclass and implement; can use database, API, or in-memory."""

    @abstractmethod
    def search_persons(self, query: str) -> list[tuple[str, dict]]:
        """Find persons where all query words appear in name. Returns (name, data)."""
        ...

    @abstractmethod
    def search_persons_by_context(self, query: str) -> list[tuple[str, dict]]:
        """Find persons where all query words appear in name or company. Returns (name, data)."""
        ...

    @abstractmethod
    def get_person(self, name: str) -> tuple[str, dict] | None:
        """Get person by exact name (case-insensitive). Returns (name, data) or None."""
        ...

    @abstractmethod
    def get_all_facilities(self) -> list[tuple[str, list[str], str]]:
        """List all facilities: (key, search_terms, info_text)."""
        ...

    @abstractmethod
    def get_facility(self, key: str) -> tuple[list[str], str] | None:
        """Get facility by key. Returns (search_terms, info_text) or None."""
        ...
