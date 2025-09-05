"""
Expanded Tagging Ontology for NFL Simulation—SportieAI
"""
TAGGING_ONTOLOGY = {
    "game_context": [
        "conversion_rate:3rd_down_high", "conversion_rate:3rd_down_low",
        "conversion_rate:4th_down_go_for_it", "conversion_rate:4th_down_punt", "conversion_rate:4th_down_field_goal",
        "clock_state:2_min_warning", "clock_state:final_drive", "clock_state:garbage_time",
        "possession_type:opening_drive", "possession_type:response_drive", "possession_type:game_winner",
        "score_margin:one_possession", "score_margin:multiple_possessions"
    ],
    "environment": [
        "stadium:arrowhead", "stadium:loud", "stadium:quiet", "stadium:indoor", "stadium:outdoor",
        "home_field_advantage:strong", "home_field_advantage:weak",
        "crowd_noise:disruptive", "crowd_noise:neutral",
        "surface:grass", "surface:turf", "surface:slippery", "weather:rain", "weather:snow", "weather:windy"
    ],
    "team_player_status": [
        "confidence:high", "confidence:shaken", "leadership:present", "leadership:absent",
        "qb_state:locked_in", "qb_state:erratic", "team_energy:surging", "team_energy:flat",
        "injury_risk:elevated", "injury_risk:low"
    ],
    "opponent": [
        "opponent:coach:aggressive", "opponent:coach:conservative",
        "opponent:defense:man_coverage", "opponent:defense:zone_blitz", "opponent:defense:cover_2", "opponent:defense:cover_3",
        "opponent:offense:spread", "opponent:offense:power_run", "opponent:offense:play_action"
    ],
    "strategy": [
        "formation:offense:shotgun", "formation:defense:nickel",
        "play_type:run_inside", "play_type:run_outside", "play_type:pass_short", "play_type:pass_deep",
        "play_design:motion", "play_design:RPO", "play_design:play_action",
        "coaching_tendency:4th_down_aggressive"
    ],
    "special_situations": [
        "penalty:drive_killer", "penalty:momentum_shift",
        "turnover:momentum_swing", "turnover:backbreaker",
        "timeout:panic", "timeout:strategic",
        "challenge:successful", "challenge:failed",
        "referee_bias:perceived", "referee_bias:none"
    ],
    "narrative_emotion": [
        "narrative:revenge_game", "narrative:rookie_debut", "narrative:legacy_drive",
        "emotion:hope", "emotion:despair", "emotion:confidence", "emotion:urgency",
        "moment:signature_play", "moment:collapse", "moment:heroics"
    ],
    "qb_deep": [
        "qb_accuracy:elite", "qb_accuracy:erratic", "qb_decision_speed:fast", "qb_decision_speed:slow",
        "qb_under_pressure:composed", "qb_under_pressure:rattled",
        "qb_completion_rate:high", "qb_completion_rate:low",
        "qb_turnover_risk:elevated", "qb_turnover_risk:low",
        "qb_red_zone_efficiency:high", "qb_red_zone_efficiency:low",
        "qb_3rd_down_conversion:clutch", "qb_3rd_down_conversion:ineffective",
        "qb_confidence:surging", "qb_confidence:shaken", "qb_leadership:strong", "qb_leadership:absent",
        "qb_body_language:positive", "qb_body_language:tense",
        "qb_throw_depth:deep", "qb_throw_depth:short",
        "qb_narrative:comeback", "qb_signature_style:gunslinger"
    ]
}

def all_tags():
    return [tag for sublist in TAGGING_ONTOLOGY.values() for tag in sublist]
