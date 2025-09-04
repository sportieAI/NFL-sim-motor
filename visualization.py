def update_dashboard(possession_state):
    wp = calculate_win_probability(possession_state)
    cluster = identify_cluster(possession_state)
    render_dashboard(possession_state, wp, cluster)