"""
The Orchestrator: Coordinates all modules for simulating a matchup.
Production-ready NFL simulation engine entry point.
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from schemas.possession_state import create_possession_state
from data.ingest_game_data import load_game_data
from strategic_cognition import seed_coach_intelligence
from logging_config import get_logger, correlation_context
from health_check import get_system_health, get_readiness
from config import config


def main():
    """Main entry point for the NFL simulation engine."""
    logger = get_logger('nfl-sim-orchestrator')
    
    # Health check first
    logger.info("Starting NFL Simulation Engine", version="1.0.0", environment=config.environment)
    
    health = get_system_health()
    if health["status"] != "healthy":
        logger.error("System health check failed", health_status=health)
        return 1
    
    readiness = get_readiness()
    if readiness["status"] != "ready":
        logger.error("System readiness check failed", readiness_status=readiness)
        return 1
    
    logger.info("System health and readiness checks passed")
    
    with correlation_context() as correlation_id:
        logger.info("Starting game simulation", correlation_id=correlation_id)
        
        try:
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
            
            logger.info("Game context configured", game_context=game_context)
            
            # 1. Ingest historical data and tendencies
            logger.info("Loading game data...")
            team_data, player_data, stadium_data = load_game_data(game_context)
            logger.info("Game data loaded successfully")
            
            # 2. Initialize possession state with context and coach profiles
            logger.info("Creating possession state...")
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
            logger.info("Possession state created", possession_state=possession_state)
        
            # 3. Seed coach intelligence for decision logic
            logger.info("Seeding coach intelligence...")
            coach_intel = seed_coach_intelligence(possession_state["coach_profile"], game_context)
            logger.info("Coach intelligence seeded", coach_intelligence=coach_intel)
            
            logger.info("NFL Simulation Engine initialized successfully", 
                       correlation_id=correlation_id,
                       game_context=game_context,
                       possession_state=possession_state,
                       coach_intelligence=coach_intel)
            
            return 0
            
        except Exception as e:
            logger.exception("Failed to initialize simulation engine", 
                           correlation_id=correlation_id,
                           error=str(e))
            return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)