"""
Tagging helpers for NFL simulation engine
"""

import pandas as pd
import numpy as np

def tag_rivalry(matchup_history):
    """
    Calculate rivalry score based on historical matchup data
    
    Args:
        matchup_history (pd.DataFrame): Historical matchup data
        
    Returns:
        float: Rivalry score between 0 and 1
    """
    if matchup_history.empty:
        return 0.5
    
    # Simple rivalry calculation based on game closeness and frequency
    close_games = len(matchup_history[abs(matchup_history.get('score_diff', 0)) <= 7])
    total_games = len(matchup_history)
    
    rivalry_score = min(1.0, (close_games / max(total_games, 1)) + (total_games / 20))
    return rivalry_score

def tag_momentum(matchup_history):
    """
    Calculate momentum shift based on recent game trends
    
    Args:
        matchup_history (pd.DataFrame): Historical matchup data
        
    Returns:
        float: Momentum score between -1 and 1
    """
    if matchup_history.empty:
        return 0.0
    
    # Calculate momentum based on recent wins/losses trend
    recent_results = matchup_history.head(3)  # Last 3 games
    if 'winner' in recent_results.columns:
        # Simple momentum calculation
        wins = len(recent_results[recent_results['winner'] == 'team_a'])
        losses = len(recent_results[recent_results['winner'] == 'team_b'])
        momentum = (wins - losses) / max(len(recent_results), 1)
        return momentum
    
    return 0.0