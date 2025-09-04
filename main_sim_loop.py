while not possession_state["drive_ended"]:
    play_call = select_play(possession_state)
    outcome = simulate_play(play_call, possession_state)
    possession_state = update_possession_state(possession_state, outcome)
    possession_state["clock"] = update_clock(possession_state["clock"], play_call["play_type"], outcome)
    if turnover_detected(outcome):
        possession_state["drive_ended"] = True
    tags = apply_tags(play_call, outcome, possession_state)
    cluster_id = cluster_play(play_call, outcome)
    memory_continuity.update(possession_state, outcome, tags)
    creative_output.narrate_snap(play_call, outcome, tags)