"""
Simulation Orchestrator
Coordinates phases, logging, analytics, RL agent, commentary, and explainability.
Enhanced with robust error handling and data-informed play selection.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple

from engine.rl_play_agent import RLPlayAgent
from engine.generative_commentary import GenerativeCommentary
from engine.advanced_analytics import AdvancedAnalytics
from engine.explainability_engine import ExplainabilityEngine
from core.exceptions import (
    ErrorEnvelope, PlayContext, PlayExecutionError, 
    StateTransitionError, PolicySelectionError, safe_execute_with_context
)
from core.play_priors import PlayPriorEngine, GameSituation, PlayType

class SimulationOrchestrator:
    def __init__(self, state_dim, action_dim, game_id: Optional[str] = None):
        self.rl_agent = RLPlayAgent(state_dim, action_dim)
        self.commentary = GenerativeCommentary()
        self.analytics = AdvancedAnalytics()
        self.explainer = ExplainabilityEngine()
        self.play_prior_engine = PlayPriorEngine()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.game_id = game_id or str(uuid.uuid4())
        self.error_log: List[ErrorEnvelope] = []
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run_simulation(self, initial_state, num_plays=100, 
                      game_situation: Optional[GameSituation] = None):
        """
        Run simulation with robust error handling and data-informed play selection.
        
        Args:
            initial_state: Initial game state
            num_plays: Number of plays to simulate
            game_situation: Optional game situation for priors computation
        """
        state = initial_state
        
        for play_number in range(num_plays):
            play_id = f"{self.game_id}-play-{play_number + 1}"
            
            # Create play context for error tracking
            play_context = PlayContext(
                play_id=play_id,
                game_id=self.game_id,
                quarter=getattr(state, 'quarter', 1) if hasattr(state, 'quarter') else 1,
                down=getattr(state, 'down', 1) if hasattr(state, 'down') else 1,
                distance=getattr(state, 'distance', 10) if hasattr(state, 'distance') else 10,
                field_position=getattr(state, 'field_position', 50) if hasattr(state, 'field_position') else 50,
                team=getattr(state, 'team', 'HOME') if hasattr(state, 'team') else 'HOME'
            )
            
            try:
                # Execute play with robustness
                success = self._execute_play_with_robustness(state, play_context, game_situation)
                
                if not success:
                    self.logger.warning(f"Play {play_id} failed, continuing with degraded state")
                    continue
                    
                # Update state for next play
                next_state, reward, done, result = self._get_last_play_result()
                
                if done:
                    self.logger.info(f"Simulation completed early at play {play_number + 1}")
                    break
                    
                state = next_state
                
            except Exception as e:
                # Top-level exception handler for catastrophic failures
                error_envelope = ErrorEnvelope(
                    play_context=play_context,
                    exception_type=type(e).__name__,
                    exception_message=str(e),
                    stacktrace=str(e),
                    timestamp=play_context.timestamp,
                    severity="critical",
                    recoverable=False
                )
                self.error_log.append(error_envelope)
                self.logger.error(f"Critical error in play {play_id}: {e}")
                
                # Decide whether to continue or abort
                if len(self.error_log) > 3:  # Too many critical errors
                    self.logger.error("Too many critical errors, aborting simulation")
                    break
        
        self._log_simulation_summary(num_plays)

    def _execute_play_with_robustness(self, state, play_context: PlayContext, 
                                     game_situation: Optional[GameSituation] = None) -> bool:
        """Execute a single play with comprehensive error handling."""
        
        # Step 1: Data-informed action selection with priors
        action, action_error = safe_execute_with_context(
            self._select_action_with_priors, play_context, state, game_situation
        )
        if action_error:
            self.error_log.append(action_error)
            action = 0  # Default fallback action
        
        # Step 2: Play simulation
        play_result, sim_error = safe_execute_with_context(
            self.simulate_play, play_context, state, action
        )
        if sim_error:
            self.error_log.append(sim_error)
            # Create fallback result
            play_result = (state, 0.0, False, {"summary": "Error during play execution", "tags": ["error"]})
        
        next_state, reward, done, result = play_result
        
        # Step 3: Store transition
        _, transition_error = safe_execute_with_context(
            self.rl_agent.store_transition, play_context, state, action, reward, next_state, done
        )
        if transition_error:
            self.error_log.append(transition_error)
        
        # Step 4: RL optimization
        _, optimize_error = safe_execute_with_context(
            self.rl_agent.optimize, play_context
        )
        if optimize_error:
            self.error_log.append(optimize_error)
        
        # Step 5: Analytics logging
        _, analytics_error = safe_execute_with_context(
            self.analytics.log_event, play_context, state, result
        )
        if analytics_error:
            self.error_log.append(analytics_error)
        
        # Step 6: Commentary generation
        commentary, comm_error = safe_execute_with_context(
            self.commentary.generate, play_context, result.get("summary", "Play occurred")
        )
        if comm_error:
            self.error_log.append(comm_error)
            commentary = "[Commentary unavailable due to error]"
        
        # Step 7: Explanation generation
        explanation, expl_error = safe_execute_with_context(
            self.explainer.explain_action, play_context, state, action, tags=result.get("tags", [])
        )
        if expl_error:
            self.error_log.append(expl_error)
            explanation = "[Explanation unavailable due to error]"
        
        # Output results
        self.logger.info(f"Play {play_context.play_id}: {result.get('summary', '')}")
        self.logger.info(f"Commentary: {commentary}")
        self.logger.info(f"Explanation: {explanation}\n")
        
        # Store results for next iteration
        self._last_play_result = (next_state, reward, done, result)
        
        return True  # Successfully executed (even with errors handled)

    def _select_action_with_priors(self, state, game_situation: Optional[GameSituation] = None) -> int:
        """Select action using RL agent with optional data-informed priors."""
        if game_situation:
            # Get play priors for the situation
            priors = self.play_prior_engine.compute_priors(game_situation)
            self.logger.debug(f"Play priors: {[(p.play_type.value, p.probability) for p in priors[:3]]}")
            
            # Use priors to influence action selection (simplified integration)
            # In a full implementation, this would integrate with the RL agent's policy
            base_action = self.rl_agent.select_action(state)
            return base_action
        else:
            return self.rl_agent.select_action(state)

    def _get_last_play_result(self) -> Tuple:
        """Get the result from the last executed play."""
        return getattr(self, '_last_play_result', (None, 0, True, {}))

    def _log_simulation_summary(self, total_plays: int):
        """Log summary of simulation including error statistics."""
        error_count = len(self.error_log)
        
        if error_count > 0:
            severity_counts = {}
            for error in self.error_log:
                severity = error.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            self.logger.info(f"Simulation completed with {error_count} errors:")
            for severity, count in severity_counts.items():
                self.logger.info(f"  {severity}: {count}")
        else:
            self.logger.info("Simulation completed successfully with no errors")

    def simulate_play(self, state, action):
        """
        Simulate a single play. Enhanced with error possibilities for robustness testing.
        """
        # Dummy simulation for demo; replace with full game logic
        
        # Simulate potential errors for testing robustness
        import random
        if random.random() < 0.05:  # 5% chance of simulation error
            raise PlayExecutionError("Simulated play execution failure", recoverable=True)
        
        next_state = state  # Should be updated with real game logic
        reward = 1.0 if action % 2 == 0 else 0.0
        done = False
        result = {"summary": f"Action {action} taken.", "tags": ["aggressive" if action % 2 == 0 else "conservative"]}
        return next_state, reward, done, result

    def get_error_log(self) -> List[ErrorEnvelope]:
        """Get the current error log for analysis."""
        return self.error_log.copy()

# Usage: orchestrator = SimulationOrchestrator(state_dim, action_dim, game_id); 
# orchestrator.run_simulation(initial_state, game_situation=situation)