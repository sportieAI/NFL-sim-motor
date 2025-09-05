"""
Test suite for simulation phase: RL play agent, analytics, commentary, explainability.
"""

from engine.simulation_orchestrator import SimulationOrchestrator

def test_run_orchestration():
    state_dim, action_dim = 10, 5
    initial_state = [0.0] * state_dim
    orchestrator = SimulationOrchestrator(state_dim, action_dim)
    orchestrator.run_simulation(initial_state, num_plays=10)

if __name__ == "__main__":
    test_run_orchestration()
    print("Simulation phase test completed.")