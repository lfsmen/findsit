import json
import os
import tempfile
from datetime import datetime, timezone

from findsit.logging.event_logger import EventLogger
from findsit.models import OccupancyEvent


def _event(event_type="activated"):
    now = datetime.now(timezone.utc)
    return OccupancyEvent(
        table_id="T01",
        row=0,
        col=0,
        previous_state=0 if event_type == "activated" else 1,
        new_state=1 if event_type == "activated" else 0,
        sensor_timestamp=now,
        gateway_timestamp=now,
        event_type=event_type,
    )


class TestEventLogger:
    def test_creates_file_if_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events.jsonl")
            with EventLogger(path) as logger:
                logger.log(_event())
            assert os.path.exists(path)

    def test_appends_one_line_per_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events.jsonl")
            with EventLogger(path) as logger:
                logger.log(_event("activated"))
                logger.log(_event("deactivated"))
            with open(path) as f:
                lines = f.readlines()
            assert len(lines) == 2

    def test_record_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events.jsonl")
            with EventLogger(path) as logger:
                logger.log(_event())
            with open(path) as f:
                record = json.loads(f.readline())
            assert record["event_type"] == "activated"
            assert record["table_id"] == "T01"

    def test_both_timestamps_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events.jsonl")
            with EventLogger(path) as logger:
                logger.log(_event())
            with open(path) as f:
                record = json.loads(f.readline())
            assert "sensor_timestamp" in record
            assert "gateway_timestamp" in record
            # Must be parseable ISO-8601
            datetime.fromisoformat(record["sensor_timestamp"])
            datetime.fromisoformat(record["gateway_timestamp"])
