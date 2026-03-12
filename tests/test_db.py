"""Unit tests for the db repository layer.

Covers MockRepository behaviour (search, get, facilities) and the db module
facade that delegates to the active repository.
"""

from db import get_all_facilities, get_facility, search_persons
from db.mock import MockRepository


class TestMockRepositorySearchPersons:
    """Corner cases for search_persons."""

    def test_empty_query_returns_empty(self) -> None:
        repo = MockRepository()
        assert repo.search_persons("") == []
        assert repo.search_persons("   ") == []
        assert repo.search_persons("\t") == []

    def test_single_word_match(self) -> None:
        repo = MockRepository()
        result = repo.search_persons("Sarah")
        assert len(result) == 1
        assert result[0][0] == "Sarah Thompson"

    def test_multiple_words_all_must_match(self) -> None:
        repo = MockRepository()
        result = repo.search_persons("John Smith")
        assert len(result) == 1
        assert result[0][0] == "John Smith"

    def test_no_match_returns_empty(self) -> None:
        repo = MockRepository()
        assert repo.search_persons("Nobody") == []

    def test_case_insensitive(self) -> None:
        repo = MockRepository()
        result = repo.search_persons("sarah thompson")
        assert len(result) == 1
        assert result[0][0] == "Sarah Thompson"


class TestMockRepositorySearchPersonsByContext:
    """Corner cases for search_persons_by_context."""

    def test_empty_query_returns_empty(self) -> None:
        repo = MockRepository()
        assert repo.search_persons_by_context("") == []
        assert repo.search_persons_by_context("   ") == []

    def test_match_by_company(self) -> None:
        repo = MockRepository()
        result = repo.search_persons_by_context("Acme")
        names = [n for n, _ in result]
        assert "Sarah Thompson" in names
        assert "John Williams" in names

    def test_match_by_name_and_company(self) -> None:
        repo = MockRepository()
        result = repo.search_persons_by_context("John Smith Engineering")
        assert len(result) == 1
        assert result[0][0] == "John Smith"


class TestMockRepositoryGetPerson:
    """Corner cases for get_person."""

    def test_empty_name_returns_none(self) -> None:
        repo = MockRepository()
        assert repo.get_person("") is None
        assert repo.get_person("   ") is None

    def test_exact_match(self) -> None:
        repo = MockRepository()
        result = repo.get_person("Sarah Thompson")
        assert result is not None
        name, data = result
        assert name == "Sarah Thompson"
        assert data["floor"] == 18
        assert data["room"] == "1801"

    def test_case_insensitive(self) -> None:
        repo = MockRepository()
        result = repo.get_person("sarah thompson")
        assert result is not None
        assert result[0] == "Sarah Thompson"

    def test_unknown_returns_none(self) -> None:
        repo = MockRepository()
        assert repo.get_person("Nobody") is None


class TestMockRepositoryGetFacility:
    """Corner cases for get_facility."""

    def test_empty_key_returns_none(self) -> None:
        repo = MockRepository()
        assert repo.get_facility("") is None
        assert repo.get_facility("   ") is None

    def test_key_normalization(self) -> None:
        repo = MockRepository()
        result = repo.get_facility("  waiting area  ")
        assert result is not None
        _, info = result
        assert "seat" in info.lower() or "lobby" in info.lower()

    def test_unknown_key_returns_none(self) -> None:
        repo = MockRepository()
        assert repo.get_facility("swimming pool") is None

    def test_facility_with_empty_search_terms(self) -> None:
        repo = MockRepository()
        result = repo.get_facility("security")
        assert result is not None
        terms, info = result
        assert terms == []
        assert "security" in info.lower()


class TestDbModuleFunctions:
    """Test db module delegates correctly to repo."""

    def test_search_persons_delegates(self) -> None:
        result = search_persons("Sarah")
        assert len(result) == 1
        assert result[0][0] == "Sarah Thompson"

    def test_get_facility_delegates(self) -> None:
        result = get_facility("bathroom")
        assert result is not None
        _, info = result
        assert "restroom" in info.lower() or "lift" in info.lower()

    def test_get_all_facilities_returns_list(self) -> None:
        result = get_all_facilities()
        assert isinstance(result, list)
        assert len(result) > 0
        key, terms, info = result[0]
        assert isinstance(key, str)
        assert isinstance(terms, list)
        assert isinstance(info, str)
