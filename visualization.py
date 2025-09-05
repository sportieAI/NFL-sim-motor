def calculate_win_probability(possession_state):
    """
    Calculate win probability based on possession state.
    Returns a probability value between 0 and 1.
    """
    # Simple win probability calculation based on field position and score
    field_position = possession_state.get("field_position", 50)
    score_diff = possession_state.get("score", {}).get(possession_state.get("team", ""), 0) - \
                possession_state.get("score", {}).get(possession_state.get("opponent", ""), 0)
    
    # Basic formula: field position advantage + score advantage
    field_advantage = (field_position - 50) / 100  # normalize to -0.5 to 0.5
    score_advantage = score_diff / 21  # normalize score difference
    
    # Base probability of 0.5 + adjustments
    win_prob = 0.5 + field_advantage + score_advantage
    
    # Clamp between 0 and 1
    return max(0.0, min(1.0, win_prob))


def identify_cluster(possession_state):
    """
    Identify which cluster the possession state belongs to.
    Returns a cluster identifier.
    """
    # Use existing cluster_play logic but adapt it for possession_state
    # Create a simplified play_call representation from possession_state
    play_call = {
        "field_position": possession_state.get("field_position", 50),
        "down": possession_state.get("down", 1),
        "distance": possession_state.get("distance", 10),
        "quarter": possession_state.get("quarter", 1)
    }
    
    # Simple clustering based on game situation
    field_pos = possession_state.get("field_position", 50)
    down = possession_state.get("down", 1)
    
    if field_pos > 80:
        return "red_zone"
    elif field_pos < 20:
        return "own_territory"
    elif down >= 3:
        return "third_down"
    else:
        return "standard_play"


def render_dashboard(possession_state, win_probability, cluster):
    """
    Render dashboard with possession state, win probability, and cluster info.
    """
    print("=== NFL Simulation Dashboard ===")
    print(f"Team: {possession_state.get('team', 'Unknown')}")
    print(f"Field Position: {possession_state.get('field_position', 'Unknown')}")
    print(f"Down: {possession_state.get('down', 'Unknown')}")
    print(f"Distance: {possession_state.get('distance', 'Unknown')}")
    print(f"Quarter: {possession_state.get('quarter', 'Unknown')}")
    print(f"Win Probability: {win_probability:.2%}")
    print(f"Play Cluster: {cluster}")
    print("=" * 32)


def update_dashboard(possession_state):
    wp = calculate_win_probability(possession_state)
    cluster = identify_cluster(possession_state)
    render_dashboard(possession_state, wp, cluster)