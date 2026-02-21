# Findsit - Seat Sensor

IoT seat occupancy detection system using Raspberry Pi and RF tags.

## Project Overview

Findsit tracks seat occupancy in real time using:
- **Sensors:** RF tags with piezoelectric sensors mounted under seats
- **Tables:** Act as relay nodes; change state to `1` when a nearby seat is occupied
- **Gateway:** Raspberry Pi that polls all table sensors, builds an occupancy matrix, and renders a heatmap

## Architecture

```
Seat (piezo + RF tag)
        │ RF
        ▼
   Table Sensor  ─── WiFi ───►  Raspberry Pi Gateway
                                     │
                                     ▼
                              Occupancy Matrix (MxN)
                              Heatmap Display
```

### Data Structures

| Entity | Format |
|--------|--------|
| Seat   | `<state>,<table_id>` |
| Table  | `<table_id>,<state>,<timestamp>` |

States: `0` = unoccupied, `1` = occupied

## Key Algorithms

**Heatmap scan** — iterate over the occupancy matrix, poll each sensor's state, update display.

**State reader** — communicate with table sensors over WiFi, read RF tag and state.

**Event logger** — on state change (activated / deactivated), record analytics and append to event log.

## Development Setup

> This project is in the planning/early-implementation phase. No build system has been established yet.

Expected stack: **Python 3** on Raspberry Pi OS.

When dependencies are introduced, install them with:

```bash
pip install -r requirements.txt
```

## Development Guidelines

- Keep sensor communication logic decoupled from display/heatmap logic.
- All state changes must be timestamped.
- The occupancy matrix dimensions (MxN) must be configurable to fit different floor plans.
- Prefer polling intervals that balance real-time accuracy against WiFi/RF congestion.
- Log every state-change event — do not discard deactivation events.

## Lint & Test

> No linter or test suite configured yet. Update this section once tooling is in place.

```bash
# Example (Python):
# flake8 .
# pytest
```
