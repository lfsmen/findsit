from __future__ import annotations

import socket
from datetime import datetime, timezone

from findsit.config import SensorConfig
from findsit.models import TableReading

READ_COMMAND = b"READ\n"


class SensorCommunicationError(Exception):
    """Raised when a sensor cannot be reached or returns malformed data."""


class SensorClient:
    """TCP client for a single table sensor. Opens a new connection per poll."""

    def __init__(self, config: SensorConfig, timeout: float) -> None:
        self._config = config
        self._timeout = timeout

    @property
    def table_id(self) -> str:
        return self._config.table_id

    def read(self) -> TableReading:
        """
        Connect to the sensor, send READ command, parse and return the response.
        Raises SensorCommunicationError on any network or parse failure.
        """
        received_at = datetime.now(timezone.utc)
        try:
            with socket.create_connection(
                (self._config.host, self._config.port), timeout=self._timeout
            ) as sock:
                sock.sendall(READ_COMMAND)
                raw = self._recv_line(sock)
        except OSError as exc:
            raise SensorCommunicationError(
                f"[{self._config.table_id}] Connection failed: {exc}"
            ) from exc

        try:
            return TableReading.from_wire(raw, received_at)
        except (ValueError, IndexError) as exc:
            raise SensorCommunicationError(
                f"[{self._config.table_id}] Malformed response {raw!r}: {exc}"
            ) from exc

    def _recv_line(self, sock: socket.socket) -> str:
        """Read bytes until newline or connection close."""
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(256)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\n" in chunk:
                break
        return b"".join(chunks).decode().strip()
