from agents.coach_agent import CoachAgent


class DefensiveAgent:
    def __init__(self, team_context, recursion_depth=0, max_depth=3):
        self.team_context = team_context
        self.recursion_depth = recursion_depth
        self.max_depth = max_depth

    def choose_defense(self, game_state):
        if game_state.get("surprise_attack") and self.recursion_depth < self.max_depth:
            coach = CoachAgent(
                self.team_context,
                recursion_depth=self.recursion_depth + 1,
                max_depth=self.max_depth,
            )
            return coach.decide_play(game_state, scenario="defense")
        if game_state.get("down") == 3:
            return "blitz"
        return "zone"
