def update_clock(clock, play_type, outcome):
    """
    Updates the game clock based on play type and outcome.
    """
    if play_type == "run":
        return clock - 40
    return clock - 30
