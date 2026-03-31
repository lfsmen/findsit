from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from findsit.logging.event_logger import EventLogger
from findsit.matrix.occupancy_matrix import OccupancyMatrix
from findsit.models import TableReading
from findsit.sensor.client import SensorClient, SensorCommunicationError

logger = logging.getLogger(__name__)


class Poller:
    """
    Drives all SensorClients concurrently on a fixed polling interval.
    On each cycle: poll all sensors → update matrix → log state changes.
    """

    def __init__(
        self,
        clients: list[SensorClient],
        matrix: OccupancyMatrix,
        event_logger: EventLogger,
        poll_interval: float,
    ) -> None:
        self._clients = clients
        self._matrix = matrix
        self._event_logger = event_logger
        self._poll_interval = poll_interval
        self._running = False

    def run(self) -> None:
        """Blocking poll loop. Call stop() from another thread or catch KeyboardInterrupt."""
        self._running = True
        while self._running:
            start = time.monotonic()
            readings = self._poll_all_concurrent()
            for result in readings:
                if isinstance(result, SensorCommunicationError):
                    logger.warning(str(result))
                    continue
                events = self._matrix.update(result)
                for event in events:
                    self._event_logger.log(event)
            elapsed = time.monotonic() - start
            sleep_for = max(0.0, self._poll_interval - elapsed)
            time.sleep(sleep_for)

    def stop(self) -> None:
        self._running = False

    def _poll_all_concurrent(self) -> list[TableReading | SensorCommunicationError]:
        results: list[TableReading | SensorCommunicationError] = []
        with ThreadPoolExecutor(max_workers=len(self._clients) or 1) as pool:
            future_to_client = {pool.submit(c.read): c for c in self._clients}
            for future in as_completed(future_to_client):
                try:
                    results.append(future.result())
                except SensorCommunicationError as exc:
                    results.append(exc)
        return results
