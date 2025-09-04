def format_for_prediction(possession_state):
    return {
        "game_id": possession_state["game_id"],
        "team": possession_state["team_id"],
        "opponent": possession_state["opponent_id"],
        "quarter": possession_state["quarter"],
        "clock": possession_state["clock"],
        "field_position": possession_state["field_position"],
        "play_sequence": possession_state["play_log"],
        "tags": possession_state["tags"],
        "cluster_id": possession_state["cluster_id"],
        "meta_feedback": possession_state["meta_learning"],
        "emotional_signal": possession_state["emotional_seed"],
        # Enhancements:
        "clustering_lineage": possession_state.get("clustering_lineage", []),
        "win_prob_delta": possession_state.get("win_prob_delta", None),
        "causal_trace": possession_state.get("causal_trace", ""),
        "integrity_hash": possession_state.get("integrity_hash", "")
    }