import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import os

# Example: External tagging helpers and API keys should be implemented separately
from utils.tagging_helpers import tag_rivalry, tag_momentum
from utils.api_keys import SPORTRADAR_KEY, FASTR_KEY

def ingest_team_data(team_id, season_year):
    """Ingest team data - falls back to demo data if API unavailable"""
    # For demo purposes, return mock data when API keys are not available
    if SPORTRADAR_KEY == 'demo_key':
        return {
            "run_ratio": 0.45 if team_id == "KC" else 0.52,
            "red_zone_efficiency": 0.67 if team_id == "KC" else 0.58,
            "team_stats": {"team_id": team_id, "season": season_year, "demo": True}
        }
    
    try:
        # Pull team-level stats from Sportradar
        url = f"https://api.sportradar.com/nfl/official/trial/v7/en/seasons/{season_year}/REG/teams/{team_id}/statistics.json?api_key={SPORTRADAR_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        # Extract tendencies
        run_ratio = data["offense"]["run_play_percentage"]
        red_zone_eff = data["offense"]["red_zone_efficiency"]
        return {
            "run_ratio": run_ratio,
            "red_zone_efficiency": red_zone_eff,
            "team_stats": data
        }
    except:
        # Fallback to demo data
        return ingest_team_data(team_id, season_year)

def ingest_player_stats(player_id, season_year):
    """Ingest player stats - falls back to demo data if API unavailable"""
    # For demo purposes, return mock data when API keys are not available
    if FASTR_KEY == 'demo_key':
        return {
            "qb_rating": 105.3 if player_id == "mahomes" else 89.2,
            "turnover_rate": 0.02 if player_id == "mahomes" else 0.03,
            "raw_stats": {"player_id": player_id, "season": season_year, "demo": True}
        }
    
    try:
        # Pull player stats from BallDontLie or SportsReference
        url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStatsByPlayerID/{season_year}/{player_id}?key={FASTR_KEY}"
        response = requests.get(url, timeout=10)
        stats = response.json()
        return {
            "qb_rating": stats.get("PassingRating", 0),
            "turnover_rate": stats.get("Fumbles", 0) / max(stats.get("Games", 1), 1),
            "raw_stats": stats
        }
    except:
        # Fallback to demo data
        return ingest_player_stats(player_id, season_year)

def ingest_stadium_conditions(stadium_name):
    # Simulate environmental context
    conditions = {
        "Arrowhead": {"wind": 12, "turf": "grass", "crowd_noise": 0.95},
        "M&T Bank": {"wind": 6, "turf": "turf", "crowd_noise": 0.88}
    }
    return conditions.get(stadium_name, {"wind": 0, "turf": "unknown", "crowd_noise": 0.5})

def ingest_historical_matchup(team_a, team_b):
    """Pull historical matchup data"""
    try:
        # Pull last 5 matchups from CSV
        csv_path = os.path.join(os.path.dirname(__file__), "historical_matchups.csv")
        matchups = pd.read_csv(csv_path)
        filtered = matchups[(matchups["team_a"] == team_a) & (matchups["team_b"] == team_b)]
        last_5 = filtered.sort_values("date", ascending=False).head(5)
        
        # Tag rivalry and momentum
        rivalry_score = tag_rivalry(last_5)
        momentum_shift = tag_momentum(last_5)
        return {
            "matchup_history": last_5.to_dict("records"),
            "rivalry_score": rivalry_score,
            "momentum_shift": momentum_shift
        }
    except Exception as e:
        print(f"Warning: Could not load historical matchups: {e}")
        return {
            "matchup_history": [],
            "rivalry_score": 0.5,
            "momentum_shift": 0.0
        }

def preprocess_data(df):
    # Normalize numerical features
    scaler = MinMaxScaler()
    numeric_cols = df.select_dtypes(include=np.number).columns
    if len(numeric_cols) > 0:
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

def load_game_data(game_context):
    """Main function to load all game data"""
    try:
        home_team = game_context["home_team"]
        away_team = game_context["away_team"] 
        stadium = game_context["stadium"]
        
        # Load team data
        home_data = ingest_team_data(home_team, 2024)
        away_data = ingest_team_data(away_team, 2024)
        
        # Load player data (using demo player IDs)
        home_qb_data = ingest_player_stats("mahomes" if home_team == "KC" else "jackson", 2024)
        away_qb_data = ingest_player_stats("jackson" if away_team == "BAL" else "mahomes", 2024)
        
        # Load stadium conditions
        stadium_data = ingest_stadium_conditions(stadium)
        
        team_data = {
            "home": home_data,
            "away": away_data,
            "historical": ingest_historical_matchup(home_team, away_team)
        }
        
        player_data = {
            "home_qb": home_qb_data,
            "away_qb": away_qb_data
        }
        
        return team_data, player_data, stadium_data
        
    except Exception as e:
        print(f"Error loading game data: {e}")
        # Return minimal demo data
        return {}, {}, {}
