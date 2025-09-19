"""
Policy Evaluator for A/B Testing Play-Selection Policies
Supports fixed random seeds for repeatability and logs outcome deltas.
"""

import random
import numpy as np
import uuid
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from core.play_priors import GameSituation


class PolicyType(Enum):
    """Types of policies that can be evaluated."""

    RL_AGENT = "rl_agent"
    PRIOR_BASED = "prior_based"
    RANDOM = "random"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"


@dataclass
class PolicyConfig:
    """Configuration for a policy being evaluated."""

    policy_id: str
    policy_type: PolicyType
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class DriveContext:
    """Context for a historical drive being replayed."""

    drive_id: str
    game_id: str
    team: str
    starting_situation: GameSituation
    historical_plays: List[Dict[str, Any]]
    actual_outcome: Dict[str, Any]  # TD, FG, Punt, Turnover, etc.


@dataclass
class PolicyOutcome:
    """Outcome from running a policy on a drive."""

    policy_id: str
    drive_id: str
    plays_executed: List[Dict[str, Any]]
    final_outcome: Dict[str, Any]
    execution_time: float
    errors: List[str]
    metrics: Dict[str, float]


@dataclass
class ComparisonResult:
    """Result of comparing two policies."""

    policy_a_id: str
    policy_b_id: str
    evaluation_id: str
    drive_count: int
    policy_a_outcomes: List[PolicyOutcome]
    policy_b_outcomes: List[PolicyOutcome]
    outcome_deltas: Dict[str, float]
    statistical_significance: Dict[str, float]
    summary: str
    timestamp: float


class PolicyEvaluator:
    """
    Evaluator for comparing play-selection policies through A/B testing.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize the evaluator.

        Args:
            random_seed: Fixed seed for reproducible evaluations
        """
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

        self.logger = logging.getLogger(__name__)
        self.evaluations: List[ComparisonResult] = []

    def run_ab_test(
        self,
        policy_a: PolicyConfig,
        policy_b: PolicyConfig,
        historical_drives: List[DriveContext],
        policy_functions: Dict[str, Callable],
        evaluation_name: str = None,
    ) -> ComparisonResult:
        """
        Run A/B test between two policies over historical drives.

        Args:
            policy_a: First policy configuration
            policy_b: Second policy configuration
            historical_drives: List of historical drives to replay
            policy_functions: Dict mapping policy_id to policy function
            evaluation_name: Optional name for this evaluation

        Returns:
            ComparisonResult with detailed comparison metrics
        """
        evaluation_id = evaluation_name or f"eval_{uuid.uuid4().hex[:8]}"

        self.logger.info(
            f"Starting A/B test {evaluation_id}: {policy_a.name} vs {policy_b.name}"
        )
        self.logger.info(f"Evaluating on {len(historical_drives)} historical drives")

        # Run both policies on all drives
        policy_a_outcomes = []
        policy_b_outcomes = []

        for drive in historical_drives:
            # Reset random seed for each drive to ensure fair comparison
            if self.random_seed is not None:
                random.seed(self.random_seed + hash(drive.drive_id))
                np.random.seed(self.random_seed + hash(drive.drive_id))

            # Run policy A
            outcome_a = self._run_policy_on_drive(
                policy_a, drive, policy_functions.get(policy_a.policy_id)
            )
            policy_a_outcomes.append(outcome_a)

            # Reset seed again for policy B
            if self.random_seed is not None:
                random.seed(self.random_seed + hash(drive.drive_id))
                np.random.seed(self.random_seed + hash(drive.drive_id))

            # Run policy B
            outcome_b = self._run_policy_on_drive(
                policy_b, drive, policy_functions.get(policy_b.policy_id)
            )
            policy_b_outcomes.append(outcome_b)

        # Compute outcome deltas and statistical significance
        outcome_deltas = self._compute_outcome_deltas(
            policy_a_outcomes, policy_b_outcomes
        )
        statistical_significance = self._compute_statistical_significance(
            policy_a_outcomes, policy_b_outcomes
        )

        # Generate summary
        summary = self._generate_comparison_summary(
            policy_a, policy_b, outcome_deltas, statistical_significance
        )

        # Create result
        result = ComparisonResult(
            policy_a_id=policy_a.policy_id,
            policy_b_id=policy_b.policy_id,
            evaluation_id=evaluation_id,
            drive_count=len(historical_drives),
            policy_a_outcomes=policy_a_outcomes,
            policy_b_outcomes=policy_b_outcomes,
            outcome_deltas=outcome_deltas,
            statistical_significance=statistical_significance,
            summary=summary,
            timestamp=time.time(),
        )

        self.evaluations.append(result)
        self.logger.info(f"A/B test {evaluation_id} completed")
        self.logger.info(f"Summary: {summary}")

        return result

    def _run_policy_on_drive(
        self, policy: PolicyConfig, drive: DriveContext, policy_function: Callable
    ) -> PolicyOutcome:
        """Run a single policy on a historical drive."""
        start_time = time.time()
        plays_executed = []
        errors = []

        try:
            # Initialize drive state
            current_situation = drive.starting_situation

            # Simulate the drive play by play
            for play_idx, historical_play in enumerate(drive.historical_plays):
                try:
                    # Get policy decision
                    if policy_function:
                        action = policy_function(current_situation, policy.parameters)
                    else:
                        action = self._default_policy_action(policy, current_situation)

                    # Simulate play outcome (simplified)
                    play_result = self._simulate_play_outcome(action, current_situation)
                    plays_executed.append(play_result)

                    # Update situation for next play
                    current_situation = self._update_situation(
                        current_situation, play_result
                    )

                    # Check if drive ended
                    if play_result.get("drive_ended", False):
                        break

                except Exception as e:
                    errors.append(f"Play {play_idx}: {str(e)}")

            # Determine final outcome
            final_outcome = self._determine_drive_outcome(
                plays_executed, drive.actual_outcome
            )

            # Compute metrics
            metrics = self._compute_drive_metrics(
                plays_executed, final_outcome, drive.actual_outcome
            )

        except Exception as e:
            errors.append(f"Drive simulation failed: {str(e)}")
            final_outcome = {"type": "ERROR", "reason": str(e)}
            metrics = {"error": 1.0}

        execution_time = time.time() - start_time

        return PolicyOutcome(
            policy_id=policy.policy_id,
            drive_id=drive.drive_id,
            plays_executed=plays_executed,
            final_outcome=final_outcome,
            execution_time=execution_time,
            errors=errors,
            metrics=metrics,
        )

    def _default_policy_action(
        self, policy: PolicyConfig, situation: GameSituation
    ) -> str:
        """Default action for policies without specific functions."""
        if policy.policy_type == PolicyType.RANDOM:
            return random.choice(["run", "pass_short", "pass_medium", "pass_deep"])
        elif policy.policy_type == PolicyType.RULE_BASED:
            # Simple rule-based logic
            if situation.down <= 2 and situation.distance <= 3:
                return "run"
            elif situation.down == 3 and situation.distance <= 7:
                return "pass_short"
            else:
                return "pass_medium"
        else:
            return "run"  # Default fallback

    def _simulate_play_outcome(
        self, action: str, situation: GameSituation
    ) -> Dict[str, Any]:
        """Simulate the outcome of a play action."""
        # Simplified simulation - would use actual game engine in practice
        yards_gained = random.randint(-5, 15)

        return {
            "action": action,
            "yards_gained": yards_gained,
            "success": (
                yards_gained >= situation.distance
                if situation.down == 3
                else yards_gained > 0
            ),
            "drive_ended": False,  # Simplified
            "turnover": random.random() < 0.02,  # 2% chance
        }

    def _update_situation(
        self, situation: GameSituation, play_result: Dict[str, Any]
    ) -> GameSituation:
        """Update game situation based on play result."""
        yards_gained = play_result.get("yards_gained", 0)
        new_field_position = min(100, situation.field_position + yards_gained)

        if play_result.get("success", False) and situation.down <= 3:
            # First down
            new_down = 1
            new_distance = 10
        else:
            new_down = situation.down + 1
            new_distance = max(1, situation.distance - yards_gained)

        return GameSituation(
            down=new_down,
            distance=new_distance,
            field_position=new_field_position,
            quarter=situation.quarter,
            time_remaining=situation.time_remaining - 45,  # Approximate play time
            score_differential=situation.score_differential,
        )

    def _determine_drive_outcome(
        self, plays: List[Dict[str, Any]], actual_outcome: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the final outcome of the drive."""
        if not plays:
            return {"type": "NO_PLAYS"}

        last_play = plays[-1]
        if last_play.get("turnover"):
            return {"type": "TURNOVER"}

        # Simplified outcome determination
        total_yards = sum(play.get("yards_gained", 0) for play in plays)
        if total_yards >= 75:  # Reached end zone
            return {"type": "TOUCHDOWN", "yards": total_yards}
        elif total_yards >= 50:  # Field goal range
            return {"type": "FIELD_GOAL", "yards": total_yards}
        else:
            return {"type": "PUNT", "yards": total_yards}

    def _compute_drive_metrics(
        self,
        plays: List[Dict[str, Any]],
        outcome: Dict[str, Any],
        actual_outcome: Dict[str, Any],
    ) -> Dict[str, float]:
        """Compute performance metrics for the drive."""
        if not plays:
            return {"plays": 0, "yards": 0, "success": 0}

        total_yards = sum(play.get("yards_gained", 0) for play in plays)
        successful_plays = sum(1 for play in plays if play.get("success", False))

        # Points scored based on outcome
        points_map = {"TOUCHDOWN": 7, "FIELD_GOAL": 3, "TURNOVER": -2, "PUNT": 0}
        points_scored = points_map.get(outcome.get("type"), 0)
        actual_points = points_map.get(actual_outcome.get("type"), 0)

        return {
            "plays": len(plays),
            "yards": total_yards,
            "yards_per_play": total_yards / len(plays),
            "successful_plays": successful_plays,
            "success_rate": successful_plays / len(plays),
            "points_scored": points_scored,
            "points_delta": points_scored - actual_points,
        }

    def _compute_outcome_deltas(
        self, outcomes_a: List[PolicyOutcome], outcomes_b: List[PolicyOutcome]
    ) -> Dict[str, float]:
        """Compute the deltas in outcomes between two policies."""
        if not outcomes_a or not outcomes_b:
            return {}

        # Aggregate metrics
        metrics_a = self._aggregate_metrics(outcomes_a)
        metrics_b = self._aggregate_metrics(outcomes_b)

        deltas = {}
        for metric in metrics_a:
            if metric in metrics_b:
                deltas[f"{metric}_delta"] = metrics_a[metric] - metrics_b[metric]
                deltas[f"{metric}_delta_pct"] = (
                    (metrics_a[metric] - metrics_b[metric]) / metrics_b[metric] * 100
                    if metrics_b[metric] != 0
                    else 0
                )

        return deltas

    def _aggregate_metrics(self, outcomes: List[PolicyOutcome]) -> Dict[str, float]:
        """Aggregate metrics across multiple outcomes."""
        if not outcomes:
            return {}

        all_metrics = {}
        for outcome in outcomes:
            for metric, value in outcome.metrics.items():
                if metric not in all_metrics:
                    all_metrics[metric] = []
                all_metrics[metric].append(value)

        # Compute means
        return {metric: np.mean(values) for metric, values in all_metrics.items()}

    def _compute_statistical_significance(
        self, outcomes_a: List[PolicyOutcome], outcomes_b: List[PolicyOutcome]
    ) -> Dict[str, float]:
        """Compute statistical significance of differences."""
        try:
            from scipy import stats
        except ImportError:
            return {"note": "scipy required for statistical significance testing"}

        if not outcomes_a or not outcomes_b:
            return {}

        significance = {}

        # Compare key metrics
        for metric in ["points_scored", "yards", "success_rate"]:
            values_a = [o.metrics.get(metric, 0) for o in outcomes_a]
            values_b = [o.metrics.get(metric, 0) for o in outcomes_b]

            if values_a and values_b:
                statistic, p_value = stats.ttest_ind(values_a, values_b)
                significance[f"{metric}_p_value"] = p_value
                significance[f"{metric}_significant"] = p_value < 0.05

        return significance

    def _generate_comparison_summary(
        self,
        policy_a: PolicyConfig,
        policy_b: PolicyConfig,
        deltas: Dict[str, float],
        significance: Dict[str, float],
    ) -> str:
        """Generate a human-readable summary of the comparison."""
        summary_parts = []

        # Points comparison
        points_delta = deltas.get("points_scored_delta", 0)
        if points_delta > 0:
            summary_parts.append(
                f"{policy_a.name} scored {points_delta:.2f} more points per drive"
            )
        elif points_delta < 0:
            summary_parts.append(
                f"{policy_b.name} scored {abs(points_delta):.2f} more points per drive"
            )
        else:
            summary_parts.append("Both policies scored similar points per drive")

        # Yards comparison
        yards_delta = deltas.get("yards_delta", 0)
        if abs(yards_delta) > 1:
            if yards_delta > 0:
                summary_parts.append(
                    f"{policy_a.name} gained {yards_delta:.1f} more yards per drive"
                )
            else:
                summary_parts.append(
                    f"{policy_b.name} gained {abs(yards_delta):.1f} more yards per drive"
                )

        # Statistical significance
        points_sig = significance.get("points_scored_significant", False)
        if points_sig:
            summary_parts.append("Difference in points is statistically significant")

        return ". ".join(summary_parts)

    def get_evaluation_history(self) -> List[ComparisonResult]:
        """Get the history of all evaluations."""
        return self.evaluations.copy()

    def export_results(self, evaluation_id: str) -> Dict[str, Any]:
        """Export detailed results for a specific evaluation."""
        for evaluation in self.evaluations:
            if evaluation.evaluation_id == evaluation_id:
                return {
                    "evaluation": asdict(evaluation),
                    "detailed_outcomes": [
                        asdict(outcome)
                        for outcome in evaluation.policy_a_outcomes
                        + evaluation.policy_b_outcomes
                    ],
                }
        return {}
