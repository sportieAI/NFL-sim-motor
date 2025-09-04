def select_play(possession_state):
    """
    Selects a play based on possession state, coach profile, crowd energy, and emotional seed.
    Returns a play_call dictionary.
    """
    # Placeholder logic; expand with coach/crowd/emotion logic
    if possession_state.get("down") == 3 and possession_state.get("distance", 10) > 5:
        play_type = "pass"
    else:
        play_type = "run"
    return {"play_type": play_type, "description": f"{play_type} play called for the moment"}