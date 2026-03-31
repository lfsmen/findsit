import pytest

from findsit.models import SeatState, TableReading


class TestSeatState:
    def test_parse_valid(self):
        s = SeatState.from_wire("1,T01")
        assert s.table_id == "T01"
        assert s.state == 1

    def test_parse_unoccupied(self):
        s = SeatState.from_wire("0,T02")
        assert s.state == 0

    def test_parse_missing_field(self):
        with pytest.raises(ValueError):
            SeatState.from_wire("1")

    def test_parse_invalid_state(self):
        with pytest.raises(ValueError):
            SeatState.from_wire("2,T01")


class TestTableReading:
    def test_parse_valid(self):
        raw = "T01,1,2026-03-14T09:00:00+00:00"
        r = TableReading.from_wire(raw)
        assert r.table_id == "T01"
        assert r.state == 1
        assert r.timestamp.year == 2026

    def test_parse_missing_field(self):
        with pytest.raises(ValueError):
            TableReading.from_wire("T01,1")

    def test_parse_invalid_state(self):
        with pytest.raises(ValueError):
            TableReading.from_wire("T01,9,2026-03-14T09:00:00+00:00")
