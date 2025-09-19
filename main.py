# The Orchestrator: Coordinates all modules for simulating a matchup.

import os
import yaml
from schemas.possession_state import create_possession_state
from data.ingest_game_data import load_game_data
from strategic_cognition import seed_coach_intelligence
from observability import logger, tracer, log_simulation_event
from reliability import publish_simulation_event
from security import require_api_key


def load_config(env: str = None):
    """Load configuration based on environment."""
    env = env or os.environ.get("NFL_SIM_ENV", "staging")
    config_path = f"config/{env}.yaml"

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            "environment": env,
            "simulation": {"randomness_enabled": True, "max_snaps_per_drive": 20},
            "logging": {"level": "INFO"},
        }


def create_game_context():
    """Create game context configuration."""
    return {
        "home_team": "KC",
        "away_team": "BAL",
        "stadium": "Arrowhead",
        "weather": "Partly Cloudy, 78°F",
        "fan_intensity": 0.92,
        "home_win_pct": 0.73,
        "rivalry_score": 0.85,
        "broadcast_slot": "Sunday Night Football",
    }


def run_simulation(config: dict, game_context: dict):
    """Run the NFL simulation with observability."""

    with tracer.trace_operation(
        "nfl_simulation",
        home_team=game_context["home_team"],
        away_team=game_context["away_team"],
    ) as span_id:

        logger.info(
            "Starting NFL simulation",
            span_id=span_id,
            home_team=game_context["home_team"],
            away_team=game_context["away_team"],
        )

        # Publish simulation start event
        publish_simulation_event(
            "simulation_started",
            {"game_context": game_context, "config": config},
            priority=1,
        )

        try:
            # 1. Ingest historical data and tendencies
            with tracer.trace_operation("data_ingestion") as data_span:
                team_data, player_data, stadium_data = load_game_data(game_context)
                log_simulation_event(
                    "data_ingested", teams_loaded=len(team_data) if team_data else 0
                )

            # 2. Initialize possession state with context and coach profiles
            with tracer.trace_operation("possession_state_init") as state_span:
                possession_state = create_possession_state(
                    home_team=game_context["home_team"],
                    away_team=game_context["away_team"],
                    crowd_energy=game_context["fan_intensity"],
                    rivalry=game_context["rivalry_score"],
                    prime_time=(
                        game_context["broadcast_slot"] == "Sunday Night Football"
                    ),
                    coach_profiles={
                        "KC": {
                            "name": "Andy Reid",
                            "aggression": 0.65,
                            "risk_tolerance": 0.60,
                            "timeout_strategy": "conservative",
                        },
                        "BAL": {
                            "name": "John Harbaugh",
                            "aggression": 0.7,
                            "risk_tolerance": 0.7,
                            "timeout_strategy": "aggressive",
                        },
                    },
                )
                log_simulation_event("possession_state_created")

            # 3. Seed coach intelligence for decision logic
            with tracer.trace_operation("coach_intelligence_init") as coach_span:
                coach_intel = seed_coach_intelligence(
                    possession_state["coach_profile"], game_context
                )
                log_simulation_event("coach_intelligence_seeded")

            # Log results
            logger.info(
                "Simulation initialization complete",
                possession_state=possession_state,
                coach_intelligence=coach_intel,
            )

            # Publish completion event
            publish_simulation_event(
                "simulation_completed",
                {"possession_state": possession_state, "coach_intel": coach_intel},
            )

            return {
                "game_context": game_context,
                "possession_state": possession_state,
                "coach_intel": coach_intel,
                "team_data": team_data,
                "player_data": player_data,
                "stadium_data": stadium_data,
            }

        except Exception as e:
            logger.error("Simulation failed", error=str(e), span_id=span_id)
            publish_simulation_event("simulation_failed", {"error": str(e)})
            raise


def main():
    """Main entry point with proper configuration and observability."""

    # Load configuration
    config = load_config()

    # Configure logging level
    import logging

    logging.getLogger().setLevel(config.get("logging", {}).get("level", "INFO"))

    logger.info(
        "NFL Simulation Engine starting",
        environment=config.get("environment", "unknown"),
        version="1.0.0",
    )

    # Create game context
    game_context = create_game_context()

    # Run simulation
    try:
        result = run_simulation(config, game_context)

        print(f"\n🏈 NFL Simulation Complete! 🏈")
        print(f"Environment: {config.get('environment', 'unknown')}")
        print(f"Game: {game_context['away_team']} @ {game_context['home_team']}")
        print(f"Stadium: {game_context['stadium']}")
        print(f"Weather: {game_context['weather']}")
        print(f"\nInitial possession state: {result['possession_state']}")
        print(f"Coach intelligence: {result['coach_intel']}")

        logger.info("Simulation completed successfully")
        return 0

    except Exception as e:
        logger.error("Simulation failed to complete", error=str(e))
        print(f"❌ Simulation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
