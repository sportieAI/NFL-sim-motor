"""
Property-based testing using Hypothesis for simulation state transitions.
Tests simulation invariants and state consistency.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

try:
    from hypothesis import given, strategies as st, settings, Verbosity
    from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize, Bundle
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False

from core.play_priors import GameSituation, PlayType
from core.exceptions import PlayContext


@dataclass
class SimulationState:
    """Represents the state of a simulation."""
    down: int
    distance: int
    field_position: int
    quarter: int
    time_remaining: int
    score_differential: int
    timeouts_remaining: int
    possession_team: str
    
    def is_valid(self) -> bool:
        """Check if state is valid."""
        return (
            1 <= self.down <= 4 and
            1 <= self.distance <= 99 and
            0 <= self.field_position <= 100 and
            1 <= self.quarter <= 4 and
            0 <= self.time_remaining <= 3600 and
            -100 <= self.score_differential <= 100 and
            0 <= self.timeouts_remaining <= 3
        )


@dataclass
class PlayAction:
    """Represents a play action."""
    play_type: str
    target_yards: int
    risk_level: float
    
    def is_valid(self) -> bool:
        """Check if action is valid."""
        return (
            self.play_type in ["run", "pass_short", "pass_medium", "pass_deep", "punt", "field_goal"] and
            -10 <= self.target_yards <= 50 and
            0.0 <= self.risk_level <= 1.0
        )


@dataclass
class PlayResult:
    """Represents the result of a play."""
    yards_gained: int
    turnover: bool
    touchdown: bool
    first_down: bool
    time_elapsed: int
    
    def is_valid(self) -> bool:
        """Check if result is valid."""
        return (
            -20 <= self.yards_gained <= 100 and
            self.time_elapsed >= 0 and
            not (self.turnover and self.touchdown)  # Can't have both
        )


class SimulationPropertyTester:
    """Property-based tester for simulation components."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not HYPOTHESIS_AVAILABLE:
            self.logger.warning("Hypothesis not available. Property-based testing disabled.")
    
    def test_game_situation_properties(self):
        """Test properties of GameSituation objects."""
        if not HYPOTHESIS_AVAILABLE:
            return
        
        @given(
            down=st.integers(min_value=1, max_value=4),
            distance=st.integers(min_value=1, max_value=99),
            field_position=st.integers(min_value=0, max_value=100),
            quarter=st.integers(min_value=1, max_value=4),
            time_remaining=st.integers(min_value=0, max_value=3600),
            score_differential=st.integers(min_value=-50, max_value=50)
        )
        def test_game_situation_validity(down, distance, field_position, quarter, time_remaining, score_differential):
            situation = GameSituation(
                down=down,
                distance=distance,
                field_position=field_position,
                quarter=quarter,
                time_remaining=time_remaining,
                score_differential=score_differential
            )
            
            # Property: Red zone flag should be consistent
            expected_redzone = field_position >= 80
            assert situation.is_redzone == expected_redzone
            
            # Property: Two-minute warning should be consistent
            expected_two_minute = time_remaining <= 120
            assert situation.is_two_minute_warning == expected_two_minute
        
        test_game_situation_validity()
    
    def test_play_context_properties(self):
        """Test properties of PlayContext objects."""
        if not HYPOTHESIS_AVAILABLE:
            return
        
        @given(
            play_id=st.text(min_size=1, max_size=50),
            game_id=st.text(min_size=1, max_size=50),
            quarter=st.integers(min_value=1, max_value=4),
            down=st.integers(min_value=1, max_value=4),
            distance=st.integers(min_value=1, max_value=99)
        )
        def test_play_context_validity(play_id, game_id, quarter, down, distance):
            context = PlayContext(
                play_id=play_id,
                game_id=game_id,
                quarter=quarter,
                down=down,
                distance=distance
            )
            
            # Property: Timestamp should be set automatically
            assert context.timestamp is not None
            assert context.timestamp <= time.time()
            
            # Property: Play ID should be preserved
            assert context.play_id == play_id
        
        test_play_context_validity()
    
    def test_simulation_state_transitions(self):
        """Test simulation state transition properties."""
        if not HYPOTHESIS_AVAILABLE:
            return
        
        @given(
            initial_state=st.builds(
                SimulationState,
                down=st.integers(1, 4),
                distance=st.integers(1, 20),
                field_position=st.integers(10, 90),
                quarter=st.integers(1, 4),
                time_remaining=st.integers(60, 3600),
                score_differential=st.integers(-30, 30),
                timeouts_remaining=st.integers(0, 3),
                possession_team=st.sampled_from(["HOME", "AWAY"])
            ),
            action=st.builds(
                PlayAction,
                play_type=st.sampled_from(["run", "pass_short", "pass_medium"]),
                target_yards=st.integers(1, 15),
                risk_level=st.floats(0.0, 1.0)
            ),
            result=st.builds(
                PlayResult,
                yards_gained=st.integers(-5, 20),
                turnover=st.booleans(),
                touchdown=st.booleans(),
                first_down=st.booleans(),
                time_elapsed=st.integers(25, 45)
            )
        )
        def test_state_transition_properties(initial_state, action, result):
            # Only test with valid inputs
            if not (initial_state.is_valid() and action.is_valid() and result.is_valid()):
                return
            
            # Simulate state transition
            new_state = self._simulate_state_transition(initial_state, action, result)
            
            # Property: Field position should be bounded
            assert 0 <= new_state.field_position <= 100
            
            # Property: Time should decrease or stay same
            assert new_state.time_remaining <= initial_state.time_remaining
            
            # Property: Down should be valid
            assert 1 <= new_state.down <= 4
            
            # Property: If touchdown, should be at end zone
            if result.touchdown:
                assert new_state.field_position >= 100 or new_state.field_position <= 0
            
            # Property: If first down achieved, down should reset to 1
            if result.first_down and not result.touchdown and not result.turnover:
                assert new_state.down == 1
        
        test_state_transition_properties()
    
    def _simulate_state_transition(self, state: SimulationState, action: PlayAction, result: PlayResult) -> SimulationState:
        """Simulate a state transition for testing."""
        new_state = SimulationState(
            down=state.down,
            distance=state.distance,
            field_position=state.field_position,
            quarter=state.quarter,
            time_remaining=max(0, state.time_remaining - result.time_elapsed),
            score_differential=state.score_differential,
            timeouts_remaining=state.timeouts_remaining,
            possession_team=state.possession_team
        )
        
        # Update field position
        new_state.field_position = max(0, min(100, state.field_position + result.yards_gained))
        
        # Handle first down
        if result.first_down or result.yards_gained >= state.distance:
            new_state.down = 1
            new_state.distance = 10
        else:
            new_state.down = min(4, state.down + 1)
            new_state.distance = max(1, state.distance - result.yards_gained)
        
        # Handle turnover
        if result.turnover:
            new_state.possession_team = "AWAY" if state.possession_team == "HOME" else "HOME"
            new_state.field_position = 100 - new_state.field_position
            new_state.down = 1
            new_state.distance = 10
        
        # Handle touchdown
        if result.touchdown:
            if state.possession_team == "HOME":
                new_state.score_differential += 7
            else:
                new_state.score_differential -= 7
        
        return new_state


if HYPOTHESIS_AVAILABLE:
    class SimulationStateMachine(RuleBasedStateMachine):
        """Stateful property-based testing for simulation state machine."""
        
        def __init__(self):
            super().__init__()
            self.game_states = []
            self.play_count = 0
        
        @initialize()
        def initialize_game(self):
            """Initialize a new game state."""
            self.current_state = SimulationState(
                down=1,
                distance=10,
                field_position=25,  # Starting field position
                quarter=1,
                time_remaining=3600,
                score_differential=0,
                timeouts_remaining=3,
                possession_team="HOME"
            )
            self.game_states.append(self.current_state)
        
        @rule(
            play_type=st.sampled_from(["run", "pass_short", "pass_medium"]),
            yards=st.integers(-5, 15)
        )
        def execute_play(self, play_type, yards):
            """Execute a play and update state."""
            # Create result
            result = PlayResult(
                yards_gained=yards,
                turnover=random.random() < 0.02,  # 2% turnover chance
                touchdown=self.current_state.field_position + yards >= 100,
                first_down=yards >= self.current_state.distance,
                time_elapsed=random.randint(25, 45)
            )
            
            # Update state
            action = PlayAction(play_type=play_type, target_yards=yards, risk_level=0.5)
            tester = SimulationPropertyTester()
            self.current_state = tester._simulate_state_transition(self.current_state, action, result)
            
            self.game_states.append(self.current_state)
            self.play_count += 1
        
        @invariant()
        def game_state_is_valid(self):
            """Game state should always be valid."""
            assert self.current_state.is_valid()
        
        @invariant()
        def time_decreases_monotonically(self):
            """Time should decrease monotonically."""
            if len(self.game_states) >= 2:
                assert self.game_states[-1].time_remaining <= self.game_states[-2].time_remaining
        
        @invariant()
        def field_position_bounded(self):
            """Field position should always be within bounds."""
            assert 0 <= self.current_state.field_position <= 100
        
        @invariant()
        def score_differential_reasonable(self):
            """Score differential should be reasonable for game duration."""
            # Very loose bounds - could be tightened based on domain knowledge
            assert -100 <= self.current_state.score_differential <= 100


def run_property_tests():
    """Run all property-based tests."""
    if not HYPOTHESIS_AVAILABLE:
        print("Hypothesis not available. Skipping property-based tests.")
        return False
    
    tester = SimulationPropertyTester()
    
    print("Running property-based tests...")
    
    try:
        # Test individual components
        tester.test_game_situation_properties()
        print("✓ GameSituation properties test passed")
        
        tester.test_play_context_properties()
        print("✓ PlayContext properties test passed")
        
        tester.test_simulation_state_transitions()
        print("✓ State transition properties test passed")
        
        # Test state machine
        print("Running stateful simulation tests...")
        state_machine_test = SimulationStateMachine.TestCase()
        state_machine_test.runTest()
        print("✓ Stateful simulation test passed")
        
        print("All property-based tests passed!")
        return True
        
    except Exception as e:
        print(f"Property-based test failed: {e}")
        return False


if __name__ == "__main__":
    run_property_tests()