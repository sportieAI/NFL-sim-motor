def apply_tags(play_call, outcome, possession_state):
    """
    Applies strategic, emotional, and predictive tags to a play.
    Returns a list of tags.
    """
    tags = []
    if possession_state.get("down") == 3 and outcome.get(
        "yards", 0
    ) >= possession_state.get("distance", 10):
        tags.append("3rd down conversion")
    if outcome.get("turnover"):
        tags.append("turnover")
    return tags
