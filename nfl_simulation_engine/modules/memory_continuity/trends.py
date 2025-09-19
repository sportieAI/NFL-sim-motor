import numpy as np


class TrendsEngine:
    def __init__(self):
        self.momentum = 0.0
        self.confidence = 0.5  # [0, 1] scale
        self.possession_trends = []  # list of dicts for each possession

    def update_momentum(self, outcome, state):
        # Example: +1 for positive yardage, -2 for turnover, +3 for TD, -1 for 3-and-out
        delta = 0
        if outcome.get("yards", 0) > 0:
            delta += 1
        if outcome.get("turnover", False):
            delta -= 2
        if outcome.get("touchdown", False):
            delta += 3
        if outcome.get("three_and_out", False):
            delta -= 1
        self.momentum += delta
        self.momentum = np.clip(self.momentum, -10, 10)
        return self.momentum

    def update_confidence(self, prediction, actual):
        # Example: Boost confidence for correct predictions, reduce for error
        if prediction == actual:
            self.confidence = min(1.0, self.confidence + 0.05)
        else:
            self.confidence = max(0.0, self.confidence - 0.05)
        return self.confidence

    def update_possession_trends(self, possession_state, outcome):
        # Track trends for each possession (e.g., avg yards, turnovers, score)
        trend = {
            "team": possession_state.get("team"),
            "yards": outcome.get("yards", 0),
            "turnover": outcome.get("turnover", False),
            "score": possession_state.get("score", 0),
        }
        self.possession_trends.append(trend)
        # Optionally aggregate statistics
        return self.possession_trends

    def get_trends_summary(self):
        # Summarize trends for display or downstream logic
        total_yards = sum([p["yards"] for p in self.possession_trends])
        turnovers = sum([1 for p in self.possession_trends if p["turnover"]])
        scores = sum([p["score"] for p in self.possession_trends])
        return {
            "momentum": self.momentum,
            "confidence": self.confidence,
            "total_yards": total_yards,
            "turnovers": turnovers,
            "scores": scores,
            "possessions": len(self.possession_trends),
        }
