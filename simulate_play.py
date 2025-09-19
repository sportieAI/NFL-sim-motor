def simulate_play(play_call, possession_state):
    """
    Simulates the outcome of a play based on play_call and possession_state.
    Returns an outcome dictionary.
    """
    import random

    outcome = {"yards": random.randint(-3, 25), "turnover": False}
    # Example logic: big play, turnover chance, etc.
    if play_call["play_type"] == "pass" and random.random() < 0.05:
        outcome["turnover"] = True
        outcome["yards"] = random.randint(-10, 0)
    return outcome
