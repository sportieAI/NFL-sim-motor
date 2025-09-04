def turnover_detected(outcome):
    """
    Returns True if a turnover occurred in the outcome.
    """
    return outcome.get('turnover', False)