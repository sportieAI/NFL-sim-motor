"""
NFL Simulation Engine - Complete Audit Example

This script demonstrates the complete workflow mentioned in the audit:
1. Install dependencies (pip install -r requirements.txt)
2. Configure meta-learning 
3. Ingest data
4. Run simulation
5. Persist data
6. Benchmark performance
7. Analyze results
"""

import config
from simulation import run_game, run_drive, run_play
from engine.persistence import save_state_to_pickle, save_state_to_sqlite, list_saved_states
from data.ingest_game_data import load_game_data, ingest_team_data, ingest_player_stats
from nfl_simulation_engine.modules.memory_continuity.meta_learning_triggers import MetaLearningTrigger
import json

def demonstrate_meta_learning_config():
    """Step 2: Configure meta-learning triggers"""
    print("\n=== Step 2: Configure Meta-Learning ===")
    
    # Enable meta-learning as described in the audit
    config.meta_learning = True
    config.triggers = {
        'high_score': {
            'condition': lambda score: score > 30,
            'action': 'optimize_strategy'
        }
    }
    
    print(f"Meta-learning enabled: {config.meta_learning}")
    print(f"Triggers configured: {list(config.triggers.keys())}")
    
    # Demonstrate meta-learning trigger usage
    def learning_callback(game_state):
        print(f"Meta-learning triggered! Optimizing strategy based on state: {game_state}")
    
    trigger = MetaLearningTrigger(learning_callback=learning_callback, check_interval=1)
    trigger.add_trigger_condition(lambda state: state.get('home_score', 0) > 21)
    
    # Test trigger
    test_state = {'home_score': 28, 'away_score': 14}
    trigger.check_and_trigger(test_state)
    
    return trigger

def demonstrate_data_ingestion():
    """Step 3: Ingest external data"""
    print("\n=== Step 3: Data Ingestion ===")
    
    # Example from the audit
    team_stats = ingest_team_data(team_id="NE", season_year=2024)
    player_stats = ingest_player_stats(player_id="1234", season_year=2024)
    
    print(f"Team stats for NE: {json.dumps(team_stats, indent=2)}")
    print(f"Player stats: {json.dumps(player_stats, indent=2)}")
    
    # Load complete game data
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
    
    team_data, player_data, stadium_data = load_game_data(game_context)
    print(f"Loaded game data successfully")
    
    return team_data, player_data, stadium_data

def demonstrate_simulation():
    """Step 4: Run simulation"""
    print("\n=== Step 4: Run Simulation ===")
    
    # Run various simulation levels
    print("Running single play...")
    play_result = run_play()
    print(f"Play result: {play_result}")
    
    print("\nRunning complete drive...")
    drive_result = run_drive()
    print(f"Drive result: {drive_result['touchdown']} (plays: {drive_result['total_plays']})")
    
    print("\nRunning complete game...")
    game_result = run_game()
    print(f"Game result: {game_result['home_score']} - {game_result['away_score']} ({game_result['winner']} wins)")
    
    return game_result

def demonstrate_persistence(game_result):
    """Step 5: Data accumulation and persistence"""
    print("\n=== Step 5: Data Persistence ===")
    
    # Pickle persistence
    pickle_file = "game_result.pkl"
    save_state_to_pickle(game_result, pickle_file)
    print(f"Saved game result to pickle: {pickle_file}")
    
    # SQLite persistence
    db_id = save_state_to_sqlite(game_result, "simulation.db")
    print(f"Saved game result to SQLite with ID: {db_id}")
    
    # List saved states
    saved_states = list_saved_states("simulation.db")
    print(f"Saved states in database: {len(saved_states)}")
    for state in saved_states[:3]:  # Show first 3
        print(f"  ID {state['id']}: {state['timestamp']}")
    
    return db_id

def demonstrate_benchmarking():
    """Step 6: Benchmark performance"""
    print("\n=== Step 6: Benchmarking ===")
    
    import time
    
    # Benchmark play simulation
    start_time = time.time()
    iterations = 100
    for _ in range(iterations):
        run_play()
    end_time = time.time()
    
    elapsed = end_time - start_time
    print(f"Executed {iterations} plays in {elapsed:.4f} seconds")
    print(f"Average time per play: {(elapsed/iterations)*1000:.2f}ms")
    
    # Benchmark drive simulation
    start_time = time.time()
    iterations = 10
    for _ in range(iterations):
        run_drive()
    end_time = time.time()
    
    elapsed = end_time - start_time
    print(f"Executed {iterations} drives in {elapsed:.4f} seconds")
    print(f"Average time per drive: {elapsed/iterations:.2f}s")

def demonstrate_analysis(game_result):
    """Step 7: Analyze results"""
    print("\n=== Step 7: Analysis & Visualization ===")
    
    # Basic analysis
    total_drives = len(game_result['drives'])
    successful_drives = sum(1 for drive in game_result['drives'] if drive['touchdown'])
    efficiency = successful_drives / total_drives if total_drives > 0 else 0
    
    print(f"Game Analysis:")
    print(f"  Total drives: {total_drives}")
    print(f"  Successful drives: {successful_drives}")
    print(f"  Drive efficiency: {efficiency:.2%}")
    print(f"  Final score: {game_result['home_score']} - {game_result['away_score']}")
    print(f"  Winner: {game_result['winner']}")
    
    # Suggest next steps
    print(f"\nNext steps for deeper analysis:")
    print(f"  - Export data to JupyterLab for interactive analysis")
    print(f"  - Use Tableau/Power BI for visualization")
    print(f"  - Run multiple simulations for statistical analysis")

def print_settings():
    """Display current configuration settings"""
    print("\n=== Configuration Settings ===")
    print("S3:", config.get_s3_settings())
    print("Mongo:", config.get_mongo_settings()) 
    print("Redis:", config.get_redis_settings())

def main():
    """Complete audit workflow demonstration"""
    print("NFL Simulation Engine - Complete Audit Workflow")
    print("=" * 50)
    
    print("\n=== Step 1: Dependencies Installed ===")
    print("✓ Dependencies installed via 'pip install -r requirements.txt'")
    
    # Run through all audit steps
    trigger = demonstrate_meta_learning_config()
    team_data, player_data, stadium_data = demonstrate_data_ingestion() 
    game_result = demonstrate_simulation()
    db_id = demonstrate_persistence(game_result)
    demonstrate_benchmarking()
    demonstrate_analysis(game_result)
    print_settings()
    
    print("\n" + "=" * 50)
    print("✓ Audit workflow completed successfully!")
    print(f"✓ Simulation data persisted (SQLite ID: {db_id})")
    print(f"✓ Meta-learning triggers configured and tested")
    print(f"✓ Benchmarking completed")
    print(f"✓ Ready for analysis in JupyterLab/Tableau/Power BI")

if __name__ == "__main__":
    main()