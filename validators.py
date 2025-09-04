def validate_snap(play_call, outcome):
    if not is_statistically_valid(outcome):
        raise ValueError("Outcome violates historical norms")
    if contains_outliers(outcome):
        log_outlier(play_call, outcome)