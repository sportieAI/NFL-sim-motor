# Tagging helpers for game context analysis

def tag_rivalry(team1, team2):
    """
    Assign rivalry score between two teams.
    In production, this would use historical data.
    """
    # Mock implementation with fallback values
    rivalry_pairs = {
        ('KC', 'BAL'): 0.85,
        ('BAL', 'KC'): 0.85,
        ('NE', 'NYJ'): 0.90,
        ('NYJ', 'NE'): 0.90,
        # Add more as needed
    }
    
    return rivalry_pairs.get((team1, team2), 0.5)  # Default moderate rivalry

def tag_momentum(game_context):
    """
    Calculate momentum score based on game context.
    Returns a value between 0 and 1.
    """
    try:
        base_momentum = 0.5
        
        # Adjust for prime time games
        if game_context.get("broadcast_slot") == "Sunday Night Football":
            base_momentum += 0.1
            
        # Adjust for fan intensity
        fan_intensity = game_context.get("fan_intensity", 0.5)
        base_momentum += (fan_intensity - 0.5) * 0.2
        
        # Keep within bounds
        return max(0.0, min(1.0, base_momentum))
        
    except Exception as e:
        print(f"Error calculating momentum: {e}")
        return 0.5  # Default neutral momentum