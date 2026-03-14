import pytest
from datetime import datetime, timezone

from findsit.matrix.occupancy_matrix import OccupancyMatrix
from findsit.models import TableReading


def _reading(table_id: str, state: int) -> TableReading:
    return TableReading(
        table_id=table_id,
        state=state,
        timestamp=datetime.now(timezone.utc),
    )


class TestOccupancyMatrix:
    def setup_method(self):
        self.matrix = OccupancyMatrix(rows=3, cols=4)
        self.matrix.register_sensor("T01", row=0, col=0)
        self.matrix.register_sensor("T02", row=1, col=2)

    def test_initial_state_zero(self):
        assert self.matrix.get_state(0, 0) == 0

    def test_update_returns_event_on_change(self):
        events = self.matrix.update(_reading("T01", 1))
        assert len(events) == 1
        assert events[0].event_type == "activated"
        assert events[0].new_state == 1
        assert events[0].previous_state == 0

    def test_update_returns_empty_on_no_change(self):
        self.matrix.update(_reading("T01", 0))
        events = self.matrix.update(_reading("T01", 0))
        assert events == []

    def test_deactivation_event(self):
        self.matrix.update(_reading("T01", 1))
        events = self.matrix.update(_reading("T01", 0))
        assert events[0].event_type == "deactivated"

    def test_snapshot_reflects_state(self):
        self.matrix.update(_reading("T01", 1))
        grid = self.matrix.snapshot()
        assert grid[0][0] == 1
        assert grid[1][2] == 0

    def test_unregistered_position_returns_zero(self):
        assert self.matrix.get_state(2, 3) == 0

    def test_register_out_of_bounds_raises(self):
        with pytest.raises(ValueError):
            self.matrix.register_sensor("T99", row=10, col=10)

    def test_update_unknown_sensor_raises(self):
        with pytest.raises(KeyError):
            self.matrix.update(_reading("UNKNOWN", 1))

    def test_invalid_dimensions_raise(self):
        with pytest.raises(ValueError):
            OccupancyMatrix(rows=0, cols=4)
