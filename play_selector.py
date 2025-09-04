def select_play(possession_state):
    """
    Selects a play based on possession state, coach profile, crowd energy, and emotional seed.
    Returns a play_call dict.
    """
    # Placeholder logic; replace with your strategic/emotional selection
    if possession_state.get('emotion', 0) > 0.7:
        return {'play_type': 'pass'}
    return {'play_type': 'run'}