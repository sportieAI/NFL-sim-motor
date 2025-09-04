def run_possession_loop(possession_state):
    while not possession_state.get("drive_ended", False):
        play_call = select_play(possession_state)
        outcome = simulate_play(play_call, possession_state)
        validators.validate_snap(play_call, outcome)
        possession_state = update_possession_state(possession_state, outcome)
        modular_reasoning.validate_causality(possession_state)
        possession_state["clock"] = update_clock(possession_state["clock"], play_call["play_type"], outcome)
        if turnover_detected(outcome):
            possession_state["drive_ended"] = True
        tags = apply_tags(play_call, outcome, possession_state)
        cluster_id = cluster_play(play_call, outcome)
        memory_continuity.update(possession_state, outcome, tags)
        meta_learning.learn_from_snap(play_call, outcome, tags)
        creative_output.narrate_snap(play_call, outcome, tags)
    # Compose, store, and broadcast signal
    formatted_data = output_formatter.format_for_prediction(possession_state)
    data_management.save(formatted_data, f"{possession_state['game_id']}_{possession_state['quarter']}.json")
    signal_router.push_to_siliconxo(formatted_data)