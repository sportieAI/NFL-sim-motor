"""
Coach Intelligence Layer: Decision logic and emotional overrides.
"""


def seed_coach_intelligence(coach_profile, game_context):
    aggression = coach_profile["aggression"]
    if game_context["rivalry_score"] > 0.8:
        aggression += 0.1  # rivalry boosts risk
    if game_context["fan_intensity"] > 0.9:
        aggression += 0.05  # crowd pressure
    return {
        "adjusted_aggression": min(aggression, 1.0),
        "decision_model": f"{coach_profile['name']} logic tree",
    }
