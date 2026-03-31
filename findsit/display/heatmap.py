from __future__ import annotations

import threading
import time
from datetime import datetime

from findsit.matrix.occupancy_matrix import OccupancyMatrix

# ANSI color codes
_RESET = "\033[0m"
_RED_BOLD = "\033[1;31m"
_GREEN = "\033[32m"
_DIM = "\033[2m"
_CLEAR_SCREEN = "\033[H\033[J"


class HeatmapDisplay:
    """
    Terminal heatmap renderer. Runs on a background daemon thread.
    Reads matrix.snapshot() at refresh_rate and redraws in place using ANSI codes.
    """

    def __init__(
        self,
        matrix: OccupancyMatrix,
        refresh_rate: float,
        color: bool = True,
    ) -> None:
        self._matrix = matrix
        self._refresh_rate = refresh_rate
        self._color = color
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._render_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._refresh_rate + 1.0)

    def _render_loop(self) -> None:
        while not self._stop_event.is_set():
            grid = self._matrix.snapshot()
            registered = self._matrix.registered_positions()
            frame = self._render_frame(grid, registered)
            print(frame, end="", flush=True)
            time.sleep(self._refresh_rate)

    def _render_frame(
        self, grid: list[list[int]], registered: set[tuple[int, int]]
    ) -> str:
        rows = len(grid)
        cols = len(grid[0]) if grid else 0
        occupied_count = sum(
            grid[r][c]
            for r in range(rows)
            for c in range(cols)
            if (r, c) in registered
        )
        total_sensors = len(registered)
        pct = (occupied_count / total_sensors * 100) if total_sensors else 0.0

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines: list[str] = [_CLEAR_SCREEN]
        lines.append(f"Findsit Occupancy Map  [{now}]\n\n")

        # Column header
        header = "     " + "  ".join(f"C{c:<2}" for c in range(cols))
        lines.append(header + "\n")

        for r in range(rows):
            row_parts = [f"R{r:<2}  "]
            for c in range(cols):
                state = grid[r][c]
                has_sensor = (r, c) in registered
                cell = self._cell(state, has_sensor)
                row_parts.append(cell)
            lines.append("  ".join(row_parts) + "\n")

        lines.append(f"\nOccupied: {occupied_count} / {total_sensors}  ({pct:.0f}%)\n")
        return "".join(lines)

    def _cell(self, state: int, has_sensor: bool) -> str:
        if not has_sensor:
            text = "[ ]"
            return f"{_DIM}{text}{_RESET}" if self._color else text
        if state == 1:
            text = "[X]"
            return f"{_RED_BOLD}{text}{_RESET}" if self._color else text
        text = "[ ]"
        return f"{_GREEN}{text}{_RESET}" if self._color else text
