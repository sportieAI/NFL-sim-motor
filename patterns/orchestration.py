"""
Orchestration best practices for simulation workflows.
"""

def orchestrate_simulation(simulator, agent, play_data):
    """
    Orchestrate a single simulation cycle.
    Args:
        simulator (NFLSimulator): The simulation engine.
        agent (SimulationAgent): The decision-making agent.
        play_data (dict): Data for the play.
    Returns:
        dict: Action and simulation result.
    """
    result = simulator.simulate_play(play_data)
    action = agent.decide_action(result)
    return {"simulation": result, "agent_action": action}