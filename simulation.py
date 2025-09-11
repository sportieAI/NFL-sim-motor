"""
Simple simulation module for benchmarking
"""

import random
import time

def run_play():
    """Simulate a single NFL play"""
    # Simple play simulation with random outcomes
    play_types = ['run', 'pass', 'punt', 'field_goal']
    play_type = random.choice(play_types)
    
    if play_type == 'run':
        yards = random.randint(-2, 15)
    elif play_type == 'pass':
        yards = random.randint(-5, 25)
    else:
        yards = 0
    
    # Simulate some processing time
    time.sleep(0.001)  # 1ms per play
    
    return {
        'play_type': play_type,
        'yards_gained': yards,
        'success': yards > 0
    }

def run_drive():
    """Simulate a complete drive"""
    plays = []
    yards_to_go = 80  # Start at 20 yard line
    down = 1
    
    while yards_to_go > 0 and down <= 4:
        play = run_play()
        plays.append(play)
        
        if play['yards_gained'] >= yards_to_go:
            # Touchdown
            break
        elif play['yards_gained'] >= (10 if down < 4 else yards_to_go):
            # First down
            yards_to_go -= play['yards_gained']
            down = 1
        else:
            # Continue drive
            yards_to_go -= play['yards_gained']
            down += 1
    
    return {
        'plays': plays,
        'touchdown': yards_to_go <= 0,
        'total_plays': len(plays)
    }

def run_game():
    """Simulate a complete game"""
    home_score = 0
    away_score = 0
    drives = []
    
    # Simulate 8 drives per team (16 total)
    for i in range(16):
        drive = run_drive()
        drives.append(drive)
        
        if drive['touchdown']:
            if i % 2 == 0:  # Home team
                home_score += 7
            else:  # Away team
                away_score += 7
    
    return {
        'home_score': home_score,
        'away_score': away_score,
        'drives': drives,
        'winner': 'home' if home_score > away_score else 'away' if away_score > home_score else 'tie'
    }