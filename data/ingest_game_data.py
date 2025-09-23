import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# Example: External tagging helpers and API keys should be implemented separately
from utils.tagging_helpers import tag_rivalry, tag_momentum
from utils.api_keys import SPORTRADAR_KEY, FASTR_KEY

def ingest_team_data(team_id, season_year):
    """
    Pull team-level stats from Sportradar with fallback to mock data.
    """
    try:
        from utils.api_keys import get_api_key, is_service_available
        
        if not is_service_available('sportradar'):
            print(f"Sportradar API not available, using mock data for {team_id}")
            return _get_mock_team_data(team_id, season_year)
            
        api_key = get_api_key('sportradar')
        url = f"https://api.sportradar.com/nfl/official/trial/v7/en/seasons/{season_year}/REG/teams/{team_id}/statistics.json?api_key={api_key}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Process and normalize the data
        return {
            "team_id": team_id,
            "season": season_year,
            "wins": data.get("wins", 8),  # Default fallback values
            "losses": data.get("losses", 8),
            "points_for": data.get("points_for", 350),
            "points_against": data.get("points_against", 300),
            "source": "sportradar_api"
        }
        
    except Exception as e:
        print(f"Error fetching team data from Sportradar: {e}")
        print(f"Falling back to mock data for {team_id}")
        return _get_mock_team_data(team_id, season_year)

def _get_mock_team_data(team_id, season_year):
    """
    Provide mock team data when external APIs are unavailable.
    """
    # Mock data based on team_id
    mock_data = {
        "KC": {"wins": 14, "losses": 3, "points_for": 445, "points_against": 320},
        "BAL": {"wins": 13, "losses": 4, "points_for": 430, "points_against": 285},
        "SF": {"wins": 12, "losses": 5, "points_for": 420, "points_against": 295},
        "BUF": {"wins": 11, "losses": 6, "points_for": 405, "points_against": 310},
    }
    
    team_stats = mock_data.get(team_id, {"wins": 8, "losses": 9, "points_for": 350, "points_against": 350})
    
    return {
        "team_id": team_id,
        "season": season_year,
        "source": "mock_data",
        **team_stats
    }

def ingest_player_stats(player_id, season_year):
    """
    Pull player stats with fallback to mock data.
    """
    try:
        from utils.api_keys import get_api_key, is_service_available
        
        if not is_service_available('fastr'):
            print(f"FASTR API not available, using mock data for player {player_id}")
            return _get_mock_player_data(player_id, season_year)
            
        api_key = get_api_key('fastr')
        url = f"https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStatsByPlayerID/{season_year}/{player_id}?key={api_key}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        stats = response.json()
        
        return {
            "qb_rating": stats.get("PassingRating", 85.0),
            "turnover_rate": stats.get("Fumbles", 0) / max(stats.get("Games", 1), 1),
            "raw_stats": stats,
            "source": "fastr_api"
        }
        
    except Exception as e:
        print(f"Error fetching player data: {e}")
        return _get_mock_player_data(player_id, season_year)

def _get_mock_player_data(player_id, season_year):
    """
    Provide mock player data when external APIs are unavailable.
    """
    return {
        "qb_rating": 85.0,
        "turnover_rate": 0.02,
        "raw_stats": {"games": 16, "passing_yards": 3500, "touchdowns": 25},
        "source": "mock_data"
    }

def ingest_stadium_conditions(stadium_name):
    # Simulate environmental context
    conditions = {
        "Arrowhead": {"wind": 12, "turf": "grass", "crowd_noise": 0.95},
        "M&T Bank": {"wind": 6, "turf": "turf", "crowd_noise": 0.88}
    }
    return conditions.get(stadium_name, {"wind": 0, "turf": "unknown", "crowd_noise": 0.5})

def ingest_historical_matchup(team_a, team_b):
    """
    Pull last 5 matchups with fallback to mock data.
    """
    try:
        # Try to read historical data
        matchups = pd.read_csv("data/historical_matchups.csv")
        filtered = matchups[(matchups["team_a"] == team_a) & (matchups["team_b"] == team_b)]
        last_5 = filtered.sort_values("date", ascending=False).head(5)
        
        if len(last_5) > 0:
            # Tag rivalry and momentum using actual data
            rivalry_score = tag_rivalry(team_a, team_b)
            momentum_shift = tag_momentum({"recent_games": last_5.to_dict("records")})
            
            return {
                "matchup_history": last_5.to_dict("records"),
                "rivalry_score": rivalry_score,
                "momentum_shift": momentum_shift,
                "source": "historical_data"
            }
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"Historical matchup data not available: {e}")
    except Exception as e:
        print(f"Error reading historical data: {e}")
    
    # Fallback to mock data
    return _get_mock_matchup_data(team_a, team_b)

def _get_mock_matchup_data(team_a, team_b):
    """
    Provide mock matchup data when historical data is unavailable.
    """
    rivalry_score = tag_rivalry(team_a, team_b)
    mock_games = [
        {"date": "2023-01-15", "winner": team_a, "score_a": 24, "score_b": 17},
        {"date": "2022-09-11", "winner": team_b, "score_a": 14, "score_b": 21},
        {"date": "2021-12-05", "winner": team_a, "score_a": 31, "score_b": 14},
    ]
    
    return {
        "matchup_history": mock_games,
        "rivalry_score": rivalry_score,
        "momentum_shift": 0.6,  # Slight advantage to team_a based on mock data
        "source": "mock_data"
    }

def preprocess_data(df):
    # Normalize numerical features
    scaler = MinMaxScaler()
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

def load_game_data(game_context):
    """
    Main function to load all game data for a simulation.
    
    Args:
        game_context: Dictionary containing game setup information
        
    Returns:
        tuple: (team_data, player_data, stadium_data)
    """
    try:
        home_team = game_context.get("home_team")
        away_team = game_context.get("away_team")
        stadium = game_context.get("stadium")
        season_year = game_context.get("season_year", "2023")
        
        print(f"Loading game data for {away_team} @ {home_team}")
        
        # Load team data
        home_team_data = ingest_team_data(home_team, season_year)
        away_team_data = ingest_team_data(away_team, season_year)
        
        team_data = {
            "home": home_team_data,
            "away": away_team_data,
            "matchup": ingest_historical_matchup(home_team, away_team)
        }
        
        # Load player data (using team IDs as placeholder player IDs)
        home_player_data = ingest_player_stats(f"{home_team}_QB", season_year)
        away_player_data = ingest_player_stats(f"{away_team}_QB", season_year)
        
        player_data = {
            "home_qb": home_player_data,
            "away_qb": away_player_data
        }
        
        # Load stadium data
        stadium_data = ingest_stadium_conditions(stadium)
        
        print(f"Game data loaded successfully")
        return team_data, player_data, stadium_data
        
    except Exception as e:
        print(f"Error loading game data: {e}")
        print("Using fallback mock data")
        
        # Return minimal mock data structure
        return (
            {"home": {"team_id": "HOME", "source": "fallback"}, 
             "away": {"team_id": "AWAY", "source": "fallback"},
             "matchup": {"rivalry_score": 0.5, "source": "fallback"}},
            {"home_qb": {"qb_rating": 85.0, "source": "fallback"}, 
             "away_qb": {"qb_rating": 85.0, "source": "fallback"}},
            {"wind": 5, "turf": "grass", "crowd_noise": 0.7, "source": "fallback"}
        )
