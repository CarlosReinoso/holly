"""Unit tests for The Shard receptionist tools."""

from unittest.mock import patch

from tools.directory import lookup_person, search_persons_for_lookup
from tools.facility import get_available_facilities, get_facility_info
from tools.weather import lookup_weather

# ---------------------------------------------------------------------------
# Directory: lookup_person
# ---------------------------------------------------------------------------


class TestLookupPerson:
    """Tests for person directory lookup."""

    def test_available_person_returns_floor_room_company(self) -> None:
        result = lookup_person("Sarah Thompson")
        assert "Floor 18" in result
        assert "1801" in result
        assert "Acme Finance" in result
        assert "available" in result.lower() or "lifts" in result.lower()

    def test_person_in_meeting_includes_lobby_suggestion(self) -> None:
        result = lookup_person("Michael Carter")
        assert "Floor 21" in result
        assert "2103" in result
        assert "Carter Legal" in result
        assert "meeting" in result.lower()
        assert "15" in result
        assert "lobby" in result.lower() or "seat" in result.lower()

    def test_person_away_offers_message_option(self) -> None:
        result = lookup_person("Emma Davis")
        assert "Emma Davis" in result
        assert "away" in result.lower() or "isn't" in result.lower()
        assert "afternoon" in result
        assert "message" in result.lower() or "reschedule" in result.lower()

    def test_person_out_to_lunch(self) -> None:
        result = lookup_person("Rachel Green")
        assert "Rachel Green" in result
        assert "lunch" in result.lower()
        assert "1pm" in result
        assert "lobby" in result.lower() or "message" in result.lower()

    def test_person_on_phone(self) -> None:
        result = lookup_person("Tom Bradley")
        assert "Tom Bradley" in result
        assert "call" in result.lower()
        assert "10" in result
        assert "seat" in result.lower() or "lobby" in result.lower()

    def test_person_do_not_disturb(self) -> None:
        result = lookup_person("Lisa Park")
        assert "Lisa Park" in result
        assert "disturb" in result.lower()
        assert "message" in result.lower() or "schedule" in result.lower()

    def test_person_in_transit(self) -> None:
        result = lookup_person("Alex Kumar")
        assert "Alex Kumar" in result
        assert "way" in result.lower() or "arriv" in result.lower()
        assert "15" in result
        assert "1915" in result
        assert "lobby" in result.lower()

    def test_unknown_person_returns_helpful_message(self) -> None:
        result = lookup_person("Nobody McNonexistent")
        assert "couldn't find" in result.lower() or "not" in result.lower()
        assert "directory" in result.lower() or "message" in result.lower()

    def test_empty_name_asks_for_clarification(self) -> None:
        result = lookup_person("")
        assert "name" in result.lower() or "who" in result.lower()

    def test_whitespace_only_name(self) -> None:
        result = lookup_person("   ")
        assert "name" in result.lower() or "who" in result.lower()

    def test_case_insensitive_lookup(self) -> None:
        result = lookup_person("sarah thompson")
        assert "Floor 18" in result
        assert "1801" in result
        assert "Acme Finance" in result

    def test_partial_name_unique_match(self) -> None:
        result = lookup_person("Sarah")
        assert "Floor 18" in result
        assert "Sarah Thompson" in result
        assert "Acme Finance" in result

    def test_multiple_matches_returns_disambiguation(self) -> None:
        result = lookup_person("John")
        assert "I found" in result and "people" in result
        assert "John Smith" in result
        assert "John Williams" in result
        assert "Smith Engineering" in result
        assert "Acme Finance" in result
        assert "Floor 14" in result or "1402" in result
        assert "Floor 20" in result or "2007" in result
        assert "Which one" in result or "visiting" in result

    def test_full_name_resolves_ambiguity(self) -> None:
        result = lookup_person("John Smith")
        assert "Floor 14" in result
        assert "1402" in result
        assert "Smith Engineering" in result
        assert "John Williams" not in result
        assert "Which one" not in result

    def test_in_meeting_with_eta_shows_minutes(self) -> None:
        """Person in meeting with meeting_eta_minutes shows specific time."""
        result = lookup_person("Sophie Brown")
        assert "meeting" in result.lower()
        assert "5" in result

    def test_in_meeting_without_eta_uses_short_while(self) -> None:
        """Person in meeting without meeting_eta_minutes uses 'a short while' fallback."""
        import db
        from db.mock import MockRepository

        repo = MockRepository()
        repo._persons["Ella Test"] = {
            "floor": 1,
            "room": "101",
            "company": "Test Co",
            "status": "in_meeting",
        }
        with patch.object(db, "_repo", repo):
            result = lookup_person("Ella Test")
        assert "meeting" in result.lower()
        assert "short while" in result.lower()

    def test_name_with_leading_trailing_spaces(self) -> None:
        """Lookup trims and finds person with padded name."""
        result = lookup_person("  Sarah Thompson  ")
        assert "Floor 18" in result
        assert "Sarah Thompson" in result

    def test_away_with_return_time(self) -> None:
        """Person away with return_time shows it (Olivia has tomorrow)."""
        result = lookup_person("Olivia Martinez")
        assert "away" in result.lower() or "isn't" in result.lower()
        assert "tomorrow" in result

    def test_away_without_return_time_uses_later(self) -> None:
        """Person away without return_time uses 'later' fallback."""
        import db
        from db.mock import MockRepository

        repo = MockRepository()
        repo._persons["Bob Away"] = {
            "floor": 1,
            "room": "102",
            "company": "Test Co",
            "status": "away",
        }
        with patch.object(db, "_repo", repo):
            result = lookup_person("Bob Away")
        assert "away" in result.lower() or "isn't" in result.lower()
        assert "later" in result.lower()


# ---------------------------------------------------------------------------
# Directory: search_persons_for_lookup
# ---------------------------------------------------------------------------


class TestSearchPersonsForLookup:
    """Tests for person search (semantic lookup)."""

    def test_search_by_name_returns_full_name_and_company(self) -> None:
        result = search_persons_for_lookup("John")
        assert "John Smith" in result
        assert "John Williams" in result
        assert "Smith Engineering" in result
        assert "Acme Finance" in result

    def test_search_by_name_and_company_narrows_match(self) -> None:
        result = search_persons_for_lookup("John Smith Engineering")
        assert "John Smith" in result
        assert "Smith Engineering" in result
        assert "John Williams" not in result

    def test_search_by_company(self) -> None:
        result = search_persons_for_lookup("Acme")
        assert (
            "Sarah Thompson" in result
            or "David Chen" in result
            or "John Williams" in result
        )
        assert "Acme Finance" in result

    def test_search_unique_name_returns_one_match(self) -> None:
        result = search_persons_for_lookup("Sarah")
        assert "Sarah Thompson" in result
        assert "Finance" in result or "Acme" in result

    def test_search_no_match_returns_helpful_message(self) -> None:
        result = search_persons_for_lookup("Nobody McNonexistent")
        assert "couldn't find" in result.lower() or "no" in result.lower()

    def test_empty_query_asks_for_clarification(self) -> None:
        result = search_persons_for_lookup("")
        assert "who" in result.lower() or "name" in result.lower()

    def test_whitespace_only_query(self) -> None:
        result = search_persons_for_lookup("   ")
        assert "who" in result.lower() or "name" in result.lower()

    def test_query_with_extra_spaces_between_words(self) -> None:
        """Multiple spaces between words still matches."""
        result = search_persons_for_lookup("John   Smith")
        assert "John Smith" in result
        assert "Smith Engineering" in result


# ---------------------------------------------------------------------------
# Facility: get_available_facilities, get_facility_info
# ---------------------------------------------------------------------------


class TestGetFacilityInfo:
    """Tests for facility information lookup."""

    def test_bathroom_directions(self) -> None:
        result = get_facility_info("bathroom")
        assert "restroom" in result.lower() or "left" in result.lower()
        assert "lift" in result.lower() or "floor" in result.lower()

    def test_toilet_maps_via_available_facilities(self) -> None:
        """LLM uses get_available_facilities to map 'toilet' -> 'bathroom'."""
        facilities = get_available_facilities()
        assert "toilet" in facilities.lower()
        assert "bathroom" in facilities.lower()
        result = get_facility_info("bathroom")
        assert "restroom" in result.lower() or "left" in result.lower()

    def test_lifts_directions(self) -> None:
        result = get_facility_info("lifts")
        assert "lift" in result.lower()
        assert "right" in result.lower()

    def test_waiting_area_info(self) -> None:
        result = get_facility_info("waiting_area")
        assert "seat" in result.lower() or "lobby" in result.lower()

    def test_waiting_area_with_space(self) -> None:
        """Key with space converts to underscore."""
        result = get_facility_info("waiting area")
        assert "seat" in result.lower() or "lobby" in result.lower()

    def test_get_available_facilities_returns_catalog(self) -> None:
        result = get_available_facilities()
        assert "bathroom" in result
        assert "lifts" in result
        assert "parking" in result
        assert "viewing_gallery" in result
        assert "toilet" in result or "loo" in result

    def test_parking_info(self) -> None:
        result = get_facility_info("parking")
        assert "park" in result.lower()
        assert "london bridge" in result.lower() or "station" in result.lower()

    def test_transport_info(self) -> None:
        result = get_facility_info("transport")
        assert "london bridge" in result.lower()
        assert "station" in result.lower() or "tube" in result.lower()

    def test_viewing_gallery_info(self) -> None:
        result = get_facility_info("viewing_gallery")
        assert "view" in result.lower() or "68" in result
        assert "lift" in result.lower()

    def test_wifi_info(self) -> None:
        result = get_facility_info("wifi")
        assert "shard" in result.lower() or "guest" in result.lower()
        assert "password" in result.lower() or "reception" in result.lower()

    def test_accessibility_info(self) -> None:
        result = get_facility_info("accessibility")
        assert "accessible" in result.lower() or "wheelchair" in result.lower()
        assert "restroom" in result.lower() or "floor" in result.lower()

    def test_emergency_info(self) -> None:
        result = get_facility_info("emergency")
        assert "emergency" in result.lower() or "fire" in result.lower()
        assert "exit" in result.lower() or "stair" in result.lower()

    def test_all_facility_keys_return_valid_info(self) -> None:
        """Every key in the catalog returns non-empty, helpful content."""
        facilities = get_available_facilities()
        lines = facilities.strip().split("\n")
        for line in lines:
            key = line.split(":")[0].strip()
            result = get_facility_info(key)
            assert len(result) > 20
            assert "get_available_facilities" not in result

    def test_unknown_facility_suggests_get_available(self) -> None:
        result = get_facility_info("swimming pool")
        assert "get_available_facilities" in result or "available" in result.lower()

    def test_empty_facility_asks_what_they_need(self) -> None:
        result = get_facility_info("")
        assert "get_available_facilities" in result or "what" in result.lower()

    def test_facility_key_with_leading_trailing_spaces(self) -> None:
        """Key with spaces is normalized and found."""
        result = get_facility_info("  bathroom  ")
        assert "restroom" in result.lower() or "left" in result.lower()

    def test_facility_key_case_insensitive(self) -> None:
        """Uppercase key normalizes and finds facility."""
        result = get_facility_info("BATHROOM")
        assert "restroom" in result.lower() or "left" in result.lower()

    def test_facility_with_no_search_terms(self) -> None:
        """Facilities with empty search terms (e.g. security) still return info."""
        result = get_facility_info("security")
        assert "security" in result.lower()
        assert len(result) > 20


# ---------------------------------------------------------------------------
# Weather: lookup_weather
# ---------------------------------------------------------------------------


class TestLookupWeather:
    """Tests for weather lookup."""

    def test_london_returns_temperature_and_conditions(self) -> None:
        result = lookup_weather("London")
        assert "degree" in result.lower() or "celsius" in result.lower()
        assert "london" in result.lower()
        assert (
            "coat" in result.lower()
            or "clear" in result.lower()
            or "cloud" in result.lower()
        )

    def test_here_defaults_to_london(self) -> None:
        result = lookup_weather("here")
        assert "london" in result.lower()
        assert "degree" in result.lower() or "celsius" in result.lower()

    def test_empty_location_defaults_to_london(self) -> None:
        result = lookup_weather("")
        assert "degree" in result.lower() or "celsius" in result.lower()

    def test_whitespace_only_defaults_to_london(self) -> None:
        result = lookup_weather("   ")
        assert "degree" in result.lower() or "celsius" in result.lower()

    def test_manchester_in_predefined_cities(self) -> None:
        result = lookup_weather("Manchester")
        assert "degree" in result.lower() or "celsius" in result.lower()
        # API may return city name or generic weather wording
        assert "manchester" in result.lower() or "coat" in result.lower()

    def test_the_shard_in_predefined(self) -> None:
        result = lookup_weather("The Shard")
        assert "degree" in result.lower() or "celsius" in result.lower()

    def test_unknown_city_handles_gracefully(self) -> None:
        result = lookup_weather("Xyzabc123nowhere")
        assert "couldn't find" in result.lower() or "london" in result.lower()

    def test_uppercase_location_normalizes(self) -> None:
        """Location like LONDON is resolved via lowercase lookup."""
        result = lookup_weather("LONDON")
        assert "london" in result.lower()
        assert "degree" in result.lower() or "celsius" in result.lower()
