def update_possession_state(possession_state, outcome):
    """
    Updates possession state based on outcome.
    """
    possession_state = possession_state.copy()
    possession_state["yards_gained"] = possession_state.get("yards_gained", 0) + outcome["yards"]
    # Advance down, update distance, field position, etc.
    possession_state["down"] = min(possession_state.get("down", 1) + 1, 4)
    possession_state["distance"] = max(1, possession_state.get("distance", 10) - outcome["yards"])
    possession_state["field_position"] = possession_state.get("field_position", 50) + outcome["yards"]
    return possession_state
