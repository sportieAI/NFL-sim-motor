import random

class NFLSimulator:
    """Deterministic, lightweight NFL play simulator for rapid prototyping."""

    def simulate_play(self, state):
        # Minimal simulation: randomly generate play outcome.
        play_id = state.get("play_id", random.randint(1, 100000))
        down = state.get("down", 1)
        yards = random.choice([0, 3, 7, 12, -2])
        description = f"Down {down}: {'Pass' if yards >= 0 else 'Run'} for {yards} yards."
        play = {
            "play_id": play_id,
            "down": down,
            "yards": yards,
            "description": description,
            "team": state.get("team", "NEP"),
            "distance": state.get("distance", 10),
            "yardline": state.get("yardline", "NEP 25"),
            "clock": state.get("clock", "15:00 Q1"),
        }
        return play
