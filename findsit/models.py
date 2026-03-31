from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class SeatState:
    """Parsed reading from a seat sensor: state + which table it is paired with."""
    table_id: str
    state: int  # 0 = unoccupied, 1 = occupied

    @classmethod
    def from_wire(cls, raw: str) -> "SeatState":
        """Parse '<state>,<table_id>' wire format."""
        parts = raw.strip().split(",", 1)
        if len(parts) != 2:
            raise ValueError(f"Expected '<state>,<table_id>', got: {raw!r}")
        state_str, table_id = parts
        state = int(state_str)
        if state not in (0, 1):
            raise ValueError(f"State must be 0 or 1, got: {state_str!r}")
        return cls(table_id=table_id.strip(), state=state)


@dataclass(frozen=True)
class TableReading:
    """Parsed response from a table sensor poll."""
    table_id: str
    state: int  # 0 = unoccupied, 1 = occupied
    timestamp: datetime  # as reported by the sensor

    @classmethod
    def from_wire(cls, raw: str, received_at: datetime | None = None) -> "TableReading":
        """Parse '<table_id>,<state>,<timestamp>' wire format."""
        parts = raw.strip().split(",", 2)
        if len(parts) != 3:
            raise ValueError(f"Expected '<table_id>,<state>,<timestamp>', got: {raw!r}")
        table_id, state_str, timestamp_str = parts
        state = int(state_str)
        if state not in (0, 1):
            raise ValueError(f"State must be 0 or 1, got: {state_str!r}")
        timestamp = datetime.fromisoformat(timestamp_str.strip())
        return cls(table_id=table_id.strip(), state=state, timestamp=timestamp)


@dataclass(frozen=True)
class OccupancyEvent:
    """A state transition detected by the occupancy matrix."""
    table_id: str
    row: int
    col: int
    previous_state: int
    new_state: int
    sensor_timestamp: datetime   # timestamp from the sensor reading
    gateway_timestamp: datetime  # when the gateway received/processed it
    event_type: Literal["activated", "deactivated"]
