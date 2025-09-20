"""
Ontology tools: tagging, versioning, drift/confidence monitoring.
"""

def tag_play(play, tag):
    """
    Tag a play with a given tag.
    Args:
        play (dict): Play data.
        tag (str): Tag string.
    Returns:
        dict: Play data with tag.
    """
    if 'tags' not in play:
        play['tags'] = []
    play['tags'].append(tag)
    return play

def monitor_drift(metrics):
    """
    Placeholder for model drift/confidence monitoring.
    """
    return {"drift_detected": False, "metrics": metrics}