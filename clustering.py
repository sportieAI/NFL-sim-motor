def cluster_play(play_call, outcome):
    """
    Assigns the play to a cluster based on features.
    Returns a cluster_id.
    """
    # Placeholder: Replace with ML clustering
    return hash(frozenset(play_call.items())) % 10
