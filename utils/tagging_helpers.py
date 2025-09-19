"""Tagging helper utilities for NFL simulation engine."""


def tag_rivalry(team1: str, team2: str) -> float:
    """Tag rivalry intensity between two teams."""
    # Placeholder implementation
    rivalry_scores = {
        ("KC", "BAL"): 0.85,
        ("BAL", "KC"): 0.85,
        ("DAL", "WAS"): 0.95,
        ("WAS", "DAL"): 0.95,
        ("GB", "CHI"): 0.90,
        ("CHI", "GB"): 0.90,
    }

    return rivalry_scores.get((team1, team2), 0.3)


def tag_momentum(score_differential: int, recent_plays: list) -> str:
    """Tag momentum based on score and recent plays."""
    # Placeholder implementation
    if score_differential > 14:
        return "strong_positive"
    elif score_differential > 7:
        return "positive"
    elif score_differential < -14:
        return "strong_negative"
    elif score_differential < -7:
        return "negative"
    else:
        return "neutral"


def tag_weather_impact(weather: str) -> dict:
    """Tag weather impact on game conditions."""
    # Placeholder implementation
    weather_lower = weather.lower()

    if "rain" in weather_lower:
        return {"condition": "wet", "passing_impact": -0.2, "rushing_impact": 0.1}
    elif "snow" in weather_lower:
        return {"condition": "snow", "passing_impact": -0.3, "rushing_impact": 0.0}
    elif "wind" in weather_lower:
        return {"condition": "windy", "passing_impact": -0.15, "rushing_impact": 0.05}
    else:
        return {"condition": "clear", "passing_impact": 0.0, "rushing_impact": 0.0}


def tag_stadium_factors(stadium: str) -> dict:
    """Tag stadium-specific factors."""
    # Placeholder implementation
    stadium_factors = {
        "Arrowhead": {"noise_level": 0.95, "home_advantage": 0.85},
        "CenturyLink": {"noise_level": 0.98, "home_advantage": 0.90},
        "Lambeau": {"noise_level": 0.80, "home_advantage": 0.88},
        "Mercedes-Benz": {"noise_level": 0.75, "home_advantage": 0.70},
    }

    return stadium_factors.get(stadium, {"noise_level": 0.70, "home_advantage": 0.65})
