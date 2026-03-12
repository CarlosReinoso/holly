"""Repository facade for directory and facility lookups.

Provides a single module-level API; currently backed by MockRepository.
Switch _repo to a DB-backed implementation for production.
"""

from db.mock import MockRepository
from db.repository import Repository

_repo: Repository = MockRepository()


def search_persons(query: str) -> list[tuple[str, dict]]:
    return _repo.search_persons(query)


def search_persons_by_context(query: str) -> list[tuple[str, dict]]:
    return _repo.search_persons_by_context(query)


def get_person(name: str) -> tuple[str, dict] | None:
    return _repo.get_person(name)


def get_all_facilities() -> list[tuple[str, list[str], str]]:
    return _repo.get_all_facilities()


def get_facility(key: str) -> tuple[list[str], str] | None:
    return _repo.get_facility(key)


__all__ = [
    "MockRepository",
    "Repository",
    "get_all_facilities",
    "get_facility",
    "get_person",
    "search_persons",
    "search_persons_by_context",
]
