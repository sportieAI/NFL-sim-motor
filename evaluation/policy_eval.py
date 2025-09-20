"""
Policy evaluation tools for agents and simulation policies.
"""

def evaluate_policy(agent, environment, episodes=10):
    """
    Evaluate agent policy in a given environment.
    Args:
        agent (SimulationAgent): The agent to test.
        environment (object): Simulation environment.
        episodes (int): Number of evaluation rounds.
    Returns:
        dict: Evaluation summary.
    """
    results = []
    for _ in range(episodes):
        state = environment.reset()
        action = agent.decide_action(state)
        results.append(action)
    return {"episodes": episodes, "actions": results}