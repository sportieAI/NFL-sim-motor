# NFL Sim Motor — Expanded Game Theater

## Overview

This simulation engine models the emotional and strategic complexity of NFL matchups, factoring in context such as rivalry, broadcast slot, crowd intensity, coach profiles, and more.

## Core Modules

- **main.py** — Orchestrates the simulation, loading context and coordinating modules.
- **schemas/possession_state.py** — Defines possession state, emotional seeds, and strategic flags.
- **data/ingest_game_data.py** — Loads historical and contextual data.
- **strategic_cognition.py** — Implements coach intelligence and decision logic.

## Example Game Context

```python
game_context = {
    "home_team": "KC",
    "away_team": "BAL",
    "stadium": "Arrowhead",
    "weather": "Partly Cloudy, 78°F",
    "fan_intensity": 0.92,
    "home_win_pct": 0.73,
    "rivalry_score": 0.85,
    "broadcast_slot": "Sunday Night Football"
}
```

## Run a Simulation

```bash
python main.py
```

---

## Emotional Seed

- **Crowd Energy**: Affects momentum, play selection, and voice synthesis tone.
- **Team Confidence**: Influences aggression and risk tolerance.
- **Rivalry Score**: Amplifies emotional resonance and strategic volatility.
- **Broadcast Slot**: Prime time games trigger higher emotional stakes.