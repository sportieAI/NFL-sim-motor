# Strategic Blueprint: Defines initial possession state with full context.

def create_possession_state(home_team, away_team, crowd_energy, rivalry, prime_time, coach_profiles):
    return {
        "team_id": home_team,
        "opponent_id": away_team,
        "quarter": 1,
        "clock": "15:00",
        "score": {"team": 0, "opponent": 0},
        "field_position": {"yardline": 25, "side": "own"},
        "emotional_seed": {
            "crowd_energy": crowd_energy,
            "team_confidence": 0.88,  # Example static, could be dynamic
            "coach_aggression": coach_profiles[home_team]["aggression"]
        },
        "coach_profile": coach_profiles[home_team],
        "context_flags": {
            "rivalry": rivalry > 0.8,
            "prime_time": prime_time
        }
    }