from __future__ import annotations

import json

from findsit.models import OccupancyEvent


class EventLogger:
    """Appends occupancy state-change events to a JSONL file."""

    def __init__(self, log_file: str) -> None:
        self._log_file = log_file
        self._file = open(log_file, "a", encoding="utf-8")

    def log(self, event: OccupancyEvent) -> None:
        """Serialize event and append one JSON line. Flushes immediately."""
        record = {
            "event_type": event.event_type,
            "table_id": event.table_id,
            "row": event.row,
            "col": event.col,
            "previous_state": event.previous_state,
            "new_state": event.new_state,
            "sensor_timestamp": event.sensor_timestamp.isoformat(),
            "gateway_timestamp": event.gateway_timestamp.isoformat(),
        }
        self._file.write(json.dumps(record) + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> "EventLogger":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
