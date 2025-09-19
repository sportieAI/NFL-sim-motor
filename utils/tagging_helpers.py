"""
Mock tagging helpers for development and testing.
In production, these would connect to real data sources.
"""

def tag_rivalry(team1: str, team2: str) -> dict:
    """Mock rivalry tagging function."""
    # Mock rivalry data based on team combinations
    rivalry_data = {
        ("KC", "BAL"): {"rivalry_score": 0.85, "historical_meetings": 12, "intensity": "high"},
        ("BAL", "KC"): {"rivalry_score": 0.85, "historical_meetings": 12, "intensity": "high"},
    }
    
    return rivalry_data.get((team1, team2), {
        "rivalry_score": 0.3, 
        "historical_meetings": 5, 
        "intensity": "low"
    })


def tag_momentum(game_context: dict) -> dict:
    """Mock momentum tagging function."""
    # Mock momentum calculation
    home_win_pct = game_context.get("home_win_pct", 0.5)
    fan_intensity = game_context.get("fan_intensity", 0.5)
    
    momentum_score = (home_win_pct + fan_intensity) / 2
    
    return {
        "momentum_score": momentum_score,
        "home_advantage": home_win_pct > 0.6,
        "crowd_factor": fan_intensity,
        "momentum_direction": "positive" if momentum_score > 0.6 else "neutral"
    }
