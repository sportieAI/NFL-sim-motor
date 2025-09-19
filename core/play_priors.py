"""
Play selection priors conditioned on game context.
Data-informed policy selection based on down, distance, time, and score.
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class PlayType(Enum):
    """Enumeration of available play types."""

    RUN = "run"
    PASS_SHORT = "pass_short"
    PASS_MEDIUM = "pass_medium"
    PASS_DEEP = "pass_deep"
    SPECIAL = "special"
    PUNT = "punt"
    FIELD_GOAL = "field_goal"


@dataclass
class GameSituation:
    """Current game situation for conditioning priors."""

    down: int
    distance: int
    field_position: int  # Yards from own goal line
    quarter: int
    time_remaining: int  # Seconds remaining in game
    score_differential: int  # Home team score - away team score
    timeouts_remaining: int = 3
    is_redzone: bool = False
    is_two_minute_warning: bool = False

    def __post_init__(self):
        self.is_redzone = self.field_position >= 80
        self.is_two_minute_warning = self.time_remaining <= 120


@dataclass
class PlayPrior:
    """Prior probability and metadata for a play type."""

    play_type: PlayType
    probability: float
    confidence: float
    reasoning: str


class PlayPriorEngine:
    """Engine for computing data-informed play selection priors."""

    def __init__(self):
        # Historical data tables (simplified for demo)
        self.historical_data = self._load_historical_data()

    def _load_historical_data(self) -> Dict[str, np.ndarray]:
        """Load historical play calling tendencies."""
        # Simplified historical data - in reality would come from NFL stats
        return {
            "run_by_down": np.array(
                [0.45, 0.35, 0.20, 0.15]
            ),  # 1st, 2nd, 3rd, 4th down
            "pass_short_by_down": np.array([0.25, 0.30, 0.35, 0.20]),
            "pass_medium_by_down": np.array([0.20, 0.25, 0.30, 0.25]),
            "pass_deep_by_down": np.array([0.10, 0.10, 0.15, 0.40]),
            "run_by_distance": {
                "short": 0.6,  # 1-3 yards
                "medium": 0.35,  # 4-7 yards
                "long": 0.15,  # 8+ yards
            },
            "redzone_multipliers": {
                PlayType.RUN: 1.5,
                PlayType.PASS_SHORT: 1.3,
                PlayType.PASS_MEDIUM: 0.8,
                PlayType.PASS_DEEP: 0.4,
            },
            "two_minute_multipliers": {
                PlayType.RUN: 0.3,
                PlayType.PASS_SHORT: 1.2,
                PlayType.PASS_MEDIUM: 1.4,
                PlayType.PASS_DEEP: 1.6,
            },
        }

    def compute_priors(self, situation: GameSituation) -> List[PlayPrior]:
        """Compute play selection priors for the given situation."""
        priors = []

        # Base probabilities from down and distance
        base_probs = self._get_base_probabilities(situation)

        # Apply situation modifiers
        adjusted_probs = self._apply_situation_modifiers(base_probs, situation)

        # Normalize to ensure probabilities sum to 1
        adjusted_probs = self._normalize_probabilities(adjusted_probs)

        # Create PlayPrior objects with reasoning
        for play_type, prob in adjusted_probs.items():
            reasoning = self._generate_reasoning(play_type, situation, prob)
            confidence = self._compute_confidence(play_type, situation)

            priors.append(
                PlayPrior(
                    play_type=play_type,
                    probability=prob,
                    confidence=confidence,
                    reasoning=reasoning,
                )
            )

        return sorted(priors, key=lambda p: p.probability, reverse=True)

    def _get_base_probabilities(
        self, situation: GameSituation
    ) -> Dict[PlayType, float]:
        """Get base probabilities from historical data."""
        down_idx = min(situation.down - 1, 3)  # Cap at 4th down

        # Distance categories
        if situation.distance <= 3:
            distance_cat = "short"
        elif situation.distance <= 7:
            distance_cat = "medium"
        else:
            distance_cat = "long"

        base_probs = {
            PlayType.RUN: self.historical_data["run_by_down"][down_idx],
            PlayType.PASS_SHORT: self.historical_data["pass_short_by_down"][down_idx],
            PlayType.PASS_MEDIUM: self.historical_data["pass_medium_by_down"][down_idx],
            PlayType.PASS_DEEP: self.historical_data["pass_deep_by_down"][down_idx],
            PlayType.SPECIAL: 0.0,
            PlayType.PUNT: 0.0,
            PlayType.FIELD_GOAL: 0.0,
        }

        # Adjust run probability based on distance
        distance_multiplier = self.historical_data["run_by_distance"][distance_cat]
        base_probs[PlayType.RUN] *= distance_multiplier

        return base_probs

    def _apply_situation_modifiers(
        self, base_probs: Dict[PlayType, float], situation: GameSituation
    ) -> Dict[PlayType, float]:
        """Apply situational modifiers to base probabilities."""
        adjusted = base_probs.copy()

        # Redzone adjustments
        if situation.is_redzone:
            for play_type, multiplier in self.historical_data[
                "redzone_multipliers"
            ].items():
                if play_type in adjusted:
                    adjusted[play_type] *= multiplier

        # Two-minute warning adjustments
        if situation.is_two_minute_warning and situation.score_differential < 0:
            for play_type, multiplier in self.historical_data[
                "two_minute_multipliers"
            ].items():
                if play_type in adjusted:
                    adjusted[play_type] *= multiplier

        # Fourth down special plays
        if situation.down == 4:
            if situation.field_position > 65 and situation.distance <= 3:
                # Go for it in opponent territory on short yardage
                adjusted[PlayType.SPECIAL] = 0.3
            elif situation.field_position > 60 and situation.field_position < 75:
                # Field goal range
                adjusted[PlayType.FIELD_GOAL] = 0.6
            else:
                # Punt
                adjusted[PlayType.PUNT] = 0.8

        return adjusted

    def _normalize_probabilities(
        self, probs: Dict[PlayType, float]
    ) -> Dict[PlayType, float]:
        """Normalize probabilities to sum to 1."""
        total = sum(probs.values())
        if total == 0:
            # Fallback to uniform distribution
            return {play_type: 1.0 / len(probs) for play_type in probs}

        return {play_type: prob / total for play_type, prob in probs.items()}

    def _generate_reasoning(
        self, play_type: PlayType, situation: GameSituation, probability: float
    ) -> str:
        """Generate human-readable reasoning for the play selection."""
        reasons = []

        if situation.down == 1:
            reasons.append("1st down provides flexibility")
        elif situation.down == 2:
            reasons.append("2nd down allows for aggressive play calling")
        elif situation.down == 3:
            reasons.append("3rd down conversion attempt")
        else:
            reasons.append("4th down critical decision")

        if situation.distance <= 3:
            reasons.append(f"short yardage ({situation.distance} yards)")
        elif situation.distance <= 7:
            reasons.append(f"manageable distance ({situation.distance} yards)")
        else:
            reasons.append(f"long distance ({situation.distance} yards)")

        if situation.is_redzone:
            reasons.append("redzone opportunity")

        if situation.is_two_minute_warning:
            reasons.append("two-minute drill situation")

        if situation.score_differential < 0:
            reasons.append("trailing in score")
        elif situation.score_differential > 0:
            reasons.append("leading in score")

        base_reasoning = f"{play_type.value} selection: " + ", ".join(reasons)
        return f"{base_reasoning} (probability: {probability:.3f})"

    def _compute_confidence(
        self, play_type: PlayType, situation: GameSituation
    ) -> float:
        """Compute confidence level for the play selection."""
        # Higher confidence for standard situations, lower for edge cases
        base_confidence = 0.7

        # Adjust based on down and distance
        if situation.down <= 2 and situation.distance <= 10:
            confidence = base_confidence + 0.2
        elif situation.down == 3 and situation.distance <= 7:
            confidence = base_confidence + 0.1
        elif situation.down == 4:
            confidence = base_confidence - 0.1
        else:
            confidence = base_confidence

        # Adjust for extreme situations
        if situation.is_two_minute_warning or situation.is_redzone:
            confidence += 0.1

        return min(1.0, max(0.1, confidence))


def get_play_priors(situation: GameSituation) -> List[PlayPrior]:
    """Convenience function to get play priors for a situation."""
    engine = PlayPriorEngine()
    return engine.compute_priors(situation)
