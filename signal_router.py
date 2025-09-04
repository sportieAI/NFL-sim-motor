def broadcast(signal):
    if not validate_signal(signal):
        raise SecurityException("Signal failed integrity check")
    log_signal(signal)
    push_to_voice_module(signal)
    push_to_music_module(signal)
    push_to_dashboard(signal)