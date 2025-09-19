from agents.coach_agent import CoachAgent


def simulate_possession(team_context, initial_state):
    coach = CoachAgent(team_context)
    game_state = initial_state
    scenarios = ["standard", "defense", "special", "critical"]
    for play in range(4):
        scenario = scenarios[play % len(scenarios)]
        call = coach.decide_play(game_state, scenario)
        print(f"Play {play+1} ({scenario}): {call}")
        # Update game_state as needed


if __name__ == "__main__":
    simulate_possession({"name": "Ravens"}, {"down": 1, "yardage": 5, "distance": 55})
