def update_possession_state(possession_state, outcome):
    """
    Updates the possession state with the outcome of a play.
    Modifies field position, down, distance, and score.
    """
    possession_state['field_position'] = possession_state.get('field_position', 25) + outcome['yards']
    # Update other fields as needed
    return possession_state
