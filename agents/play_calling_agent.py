from agents.coach_agent import CoachAgent


class PlayCallingAgent:
    def __init__(self, team_context, recursion_depth=0, max_depth=3):
        self.team_context = team_context
        self.recursion_depth = recursion_depth
        self.max_depth = max_depth

    def suggest_play(self, game_state):
        if game_state.get("chaos_mode") and self.recursion_depth < self.max_depth:
            coach = CoachAgent(
                self.team_context,
                recursion_depth=self.recursion_depth + 1,
                max_depth=self.max_depth,
            )
            return coach.decide_play(game_state, scenario="critical")
        if game_state.get("yardage") > 10:
            return "deep_pass"
        return "short_run"
