#!/usr/bin/env python3
"""Findsit gateway — entry point."""
from __future__ import annotations

import logging
import signal
import sys

from findsit.config import Config
from findsit.display.heatmap import HeatmapDisplay
from findsit.logging.event_logger import EventLogger
from findsit.matrix.occupancy_matrix import OccupancyMatrix
from findsit.sensor.client import SensorClient
from findsit.sensor.poller import Poller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    log.info("Loading config from %s", config_path)
    config = Config.load(config_path)

    matrix = OccupancyMatrix(config.rows, config.cols)
    clients: list[SensorClient] = []

    for sensor_cfg in config.sensors:
        matrix.register_sensor(sensor_cfg.table_id, sensor_cfg.row, sensor_cfg.col)
        clients.append(SensorClient(sensor_cfg, config.sensor_timeout_seconds))

    log.info(
        "Registered %d sensor(s) on a %dx%d grid",
        len(clients), config.rows, config.cols,
    )

    event_logger = EventLogger(config.log_file)
    display = HeatmapDisplay(matrix, config.display_refresh_rate, config.display_color)
    poller = Poller(clients, matrix, event_logger, config.poll_interval_seconds)

    def _shutdown(signum: int, frame: object) -> None:  # noqa: ARG001
        log.info("Shutting down…")
        poller.stop()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    display.start()
    try:
        poller.run()
    finally:
        display.stop()
        event_logger.close()
        log.info("Findsit stopped.")


if __name__ == "__main__":
    main()
