🟡 The Orchestrator: Coordinates all modules for simulating a matchup.

from schemas.possession_state import create_possession_state
from data.ingest_game_data import load_game_data
from strategic_cognition import seed_coach_intelligence

# Game context configuration
game_context = {
    "home_team": "KC",
    "away_team": "BAL",
    "stadium": "Arrowhead",
    "weather": "Partly Cloudy, 78°F",
    "fan_intensity": 0.92,
    "home_win_pct": 0.73,
    "rivalry_score": 0.85,
    "broadcast_slot": "Sunday Night Football"
}

if __name__ == "__main__":
    # 1. Ingest historical data and tendencies
    team_data, player_data, stadium_data = load_game_data(game_context)
    
    # 2. Initialize possession state with context and coach profiles
    possession_state = create_possession_state(
        home_team=game_context["home_team"],
        away_team=game_context["away_team"],
        crowd_energy=game_context["fan_intensity"],
        rivalry=game_context["rivalry_score"],
        prime_time=(game_context["broadcast_slot"] == "Sunday Night Football"),
        coach_profiles={
            "KC": {"name": "Andy Reid", "aggression": 0.65, "risk_tolerance": 0.60, "timeout_strategy": "conservative"},
            "BAL": {"name": "John Harbaugh", "aggression": 0.7, "risk_tolerance": 0.7, "timeout_strategy": "aggressive"},
        }
    )

    # 3. Seed coach intelligence for decision logic
    coach_intel = seed_coach_intelligence(possession_state["coach_profile"], game_context)
    
    print("Game context:", game_context)
    print("Initial possession state:", possession_state)
    print("Coach intelligence:", coach_intel)