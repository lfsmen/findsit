from __future__ import annotations

from datetime import datetime, timezone

from findsit.models import OccupancyEvent, TableReading


class OccupancyMatrix:
    """MxN grid tracking current occupancy state of all registered table sensors."""

    def __init__(self, rows: int, cols: int) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError(f"Grid dimensions must be positive, got {rows}x{cols}")
        self._rows = rows
        self._cols = cols
        # table_id -> current state (0 or 1)
        self._states: dict[str, int] = {}
        # table_id -> (row, col)
        self._positions: dict[str, tuple[int, int]] = {}

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def register_sensor(self, table_id: str, row: int, col: int) -> None:
        """Register a sensor's position in the grid. Must be called before update()."""
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            raise ValueError(
                f"Position ({row}, {col}) out of bounds for {self._rows}x{self._cols} grid"
            )
        occupied = [(r, c) for tid, (r, c) in self._positions.items() if tid != table_id]
        if (row, col) in occupied:
            raise ValueError(f"Position ({row}, {col}) already registered by another sensor")
        self._positions[table_id] = (row, col)
        self._states.setdefault(table_id, 0)

    def update(self, reading: TableReading) -> list[OccupancyEvent]:
        """
        Apply a new sensor reading. Returns a list with one OccupancyEvent if the
        state changed, or an empty list if the state is unchanged.
        """
        if reading.table_id not in self._positions:
            raise KeyError(f"Sensor '{reading.table_id}' is not registered")

        previous = self._states[reading.table_id]
        if reading.state == previous:
            return []

        self._states[reading.table_id] = reading.state
        row, col = self._positions[reading.table_id]
        event_type = "activated" if reading.state == 1 else "deactivated"
        return [
            OccupancyEvent(
                table_id=reading.table_id,
                row=row,
                col=col,
                previous_state=previous,
                new_state=reading.state,
                sensor_timestamp=reading.timestamp,
                gateway_timestamp=datetime.now(timezone.utc),
                event_type=event_type,
            )
        ]

    def get_state(self, row: int, col: int) -> int:
        """Return current state at (row, col). Returns 0 for positions with no sensor."""
        for table_id, (r, c) in self._positions.items():
            if r == row and c == col:
                return self._states.get(table_id, 0)
        return 0

    def snapshot(self) -> list[list[int]]:
        """Return a rows x cols 2D list of current states (0 for unregistered positions)."""
        grid = [[0] * self._cols for _ in range(self._rows)]
        for table_id, (row, col) in self._positions.items():
            grid[row][col] = self._states.get(table_id, 0)
        return grid

    def registered_positions(self) -> set[tuple[int, int]]:
        """Return the set of (row, col) positions that have a registered sensor."""
        return set(self._positions.values())
