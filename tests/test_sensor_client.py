import pytest

from findsit.config import SensorConfig
from findsit.sensor.client import SensorClient, SensorCommunicationError
from tests.fixtures.mock_sensor_responses import MockSensorServer

_PORT = 19901


class TestSensorClient:
    def setup_method(self):
        self.server = MockSensorServer("T01", port=_PORT, initial_state=0)
        self.server.start()
        self.cfg = SensorConfig(
            table_id="T01", host="127.0.0.1", port=_PORT, row=0, col=0
        )
        self.client = SensorClient(self.cfg, timeout=2.0)

    def teardown_method(self):
        self.server.stop()

    def test_read_returns_table_reading(self):
        reading = self.client.read()
        assert reading.table_id == "T01"
        assert reading.state == 0

    def test_read_reflects_updated_state(self):
        self.server.set_state(1)
        reading = self.client.read()
        assert reading.state == 1

    def test_connection_refused_raises_communication_error(self):
        bad_cfg = SensorConfig(
            table_id="T99", host="127.0.0.1", port=19999, row=0, col=0
        )
        client = SensorClient(bad_cfg, timeout=0.5)
        with pytest.raises(SensorCommunicationError):
            client.read()
