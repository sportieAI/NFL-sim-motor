def narrate_snap(play_call, outcome, tags):
    validated = validate_outcome_against_real_data(play_call, outcome)
    if not validated:
        raise ValueError("Outcome not statistically plausible")

    emotion = derive_emotional_signal(tags)
    voice = synthesize_voice(play_call, outcome, emotion)
    music = generate_music(emotion)
    return voice, music