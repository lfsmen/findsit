"""
Mock TCP server that mimics a table sensor for use in tests.

Usage:
    server = MockSensorServer("T01", port=19001)
    server.start()
    # ... run test ...
    server.stop()
"""
from __future__ import annotations

import socket
import threading
from datetime import datetime, timezone


class MockSensorServer:
    """Listens on a local TCP port and returns scripted sensor responses."""

    READ_COMMAND = b"READ\n"

    def __init__(self, table_id: str, port: int, initial_state: int = 0) -> None:
        self.table_id = table_id
        self.port = port
        self._state = initial_state
        self._lock = threading.Lock()
        self._server_socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def set_state(self, state: int) -> None:
        with self._lock:
            self._state = state

    def start(self) -> None:
        self._stop_event.clear()
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(("127.0.0.1", self.port))
        self._server_socket.listen(5)
        self._server_socket.settimeout(0.5)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
        if self._thread:
            self._thread.join(timeout=2.0)

    def _serve(self) -> None:
        while not self._stop_event.is_set():
            try:
                conn, _ = self._server_socket.accept()  # type: ignore[union-attr]
            except (socket.timeout, OSError):
                continue
            try:
                self._handle(conn)
            finally:
                conn.close()

    def _handle(self, conn: socket.socket) -> None:
        conn.settimeout(1.0)
        try:
            data = conn.recv(1024)
        except socket.timeout:
            return
        if not data:
            return
        with self._lock:
            state = self._state
        timestamp = datetime.now(timezone.utc).isoformat()
        response = f"{self.table_id},{state},{timestamp}\n"
        conn.sendall(response.encode())
