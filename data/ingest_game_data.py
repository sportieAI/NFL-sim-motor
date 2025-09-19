import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# Example: External tagging helpers and API keys should be implemented separately
from utils.tagging_helpers import tag_rivalry, tag_momentum
from utils.api_keys import SPORTRADAR_KEY, FASTR_KEY


def ingest_team_data(team_id, season_year):
    # Pull team-level stats from Sportradar
    url = f"https://api.sportradar.com/nfl/official/trial/v7/en/seasons/{season_year}/REG/teams/{team_id}/statistics.json?api_key={SPORTRADAR_KEY}"
    response = requests.get(url)
    data = response.json()
    # Extract tendencies
    run_ratio = data["offense"]["run_play_percentage"]
    red_zone_eff = data["offense"]["red_zone_efficiency"]
    return {
        "run_ratio": run_ratio,
        "red_zone_efficiency": red_zone_eff,
        "team_stats": data,
    }


def ingest_player_stats(player_id, season_year):
    # Pull player stats from BallDontLie or SportsReference
    url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStatsByPlayerID/{season_year}/{player_id}?key={FASTR_KEY}"
    response = requests.get(url)
    stats = response.json()
    return {
        "qb_rating": stats.get("PassingRating", 0),
        "turnover_rate": stats.get("Fumbles", 0) / max(stats.get("Games", 1), 1),
        "raw_stats": stats,
    }


def ingest_stadium_conditions(stadium_name):
    # Simulate environmental context
    conditions = {
        "Arrowhead": {"wind": 12, "turf": "grass", "crowd_noise": 0.95},
        "M&T Bank": {"wind": 6, "turf": "turf", "crowd_noise": 0.88},
    }
    return conditions.get(
        stadium_name, {"wind": 0, "turf": "unknown", "crowd_noise": 0.5}
    )


def ingest_historical_matchup(team_a, team_b):
    # Pull last 5 matchups from Pro Football Reference
    matchups = pd.read_csv("data/historical_matchups.csv")
    filtered = matchups[(matchups["team_a"] == team_a) & (matchups["team_b"] == team_b)]
    last_5 = filtered.sort_values("date", ascending=False).head(5)
    # Tag rivalry and momentum
    rivalry_score = tag_rivalry(last_5)
    momentum_shift = tag_momentum(last_5)
    return {
        "matchup_history": last_5.to_dict("records"),
        "rivalry_score": rivalry_score,
        "momentum_shift": momentum_shift,
    }


def preprocess_data(df):
    # Normalize numerical features
    scaler = MinMaxScaler()
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df


def load_game_data(game_context):
    """Load and aggregate all game data for simulation."""
    try:
        # Extract team IDs from context
        home_team = game_context.get("home_team", "KC")
        away_team = game_context.get("away_team", "BAL")
        season_year = game_context.get("season_year", 2024)

        # Load team data (with mock data for demo)
        team_data = {
            home_team: {
                "run_ratio": 0.45,
                "red_zone_efficiency": 0.78,
                "team_stats": {"offense": {"yards_per_game": 350}},
            },
            away_team: {
                "run_ratio": 0.52,
                "red_zone_efficiency": 0.71,
                "team_stats": {"offense": {"yards_per_game": 320}},
            },
        }

        # Load player data (mock)
        player_data = {
            "quarterbacks": {
                home_team: {"name": "Patrick Mahomes", "rating": 105.2},
                away_team: {"name": "Lamar Jackson", "rating": 101.8},
            },
            "running_backs": {
                home_team: {"name": "Isiah Pacheco", "yards_per_carry": 4.2},
                away_team: {"name": "Derrick Henry", "yards_per_carry": 4.8},
            },
        }

        # Load stadium data
        stadium_data = ingest_stadium_context(game_context)

        return team_data, player_data, stadium_data

    except Exception as e:
        # Return mock data if external APIs fail
        print(f"Warning: Could not load external data ({e}), using mock data")
        return {}, {}, {}
