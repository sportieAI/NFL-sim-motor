def learn_from_snap(play_call, outcome, tags):
    cluster_id = identify_cluster(play_call, outcome)
    reward_signal = calculate_reward(outcome, tags)
    update_strategy_model(cluster_id, reward_signal)