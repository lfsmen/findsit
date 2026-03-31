from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class SensorConfig:
    table_id: str
    host: str
    port: int
    row: int
    col: int


@dataclass
class Config:
    rows: int
    cols: int
    poll_interval_seconds: float
    sensor_timeout_seconds: float
    display_refresh_rate: float
    display_color: bool
    log_file: str
    sensors: list[SensorConfig] = field(default_factory=list)

    @classmethod
    def load(cls, path: str) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Config":
        sensors = [
            SensorConfig(
                table_id=s["table_id"],
                host=s["host"],
                port=s["port"],
                row=s["row"],
                col=s["col"],
            )
            for s in d.get("sensors", [])
        ]
        return cls(
            rows=d["matrix"]["rows"],
            cols=d["matrix"]["cols"],
            poll_interval_seconds=d["polling"]["interval_seconds"],
            sensor_timeout_seconds=d["polling"]["sensor_timeout_seconds"],
            display_refresh_rate=d["display"]["refresh_rate_seconds"],
            display_color=d["display"].get("color", True),
            log_file=d["logging"]["log_file"],
            sensors=sensors,
        )
