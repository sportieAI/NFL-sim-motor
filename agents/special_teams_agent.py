class SpecialTeamsAgent:
    def __init__(self, team_context, recursion_depth=0, max_depth=3):
        self.team_context = team_context
        self.recursion_depth = recursion_depth
        self.max_depth = max_depth

    def select_special_teams_play(self, game_state):
        if game_state.get("fake_punt") and self.recursion_depth < self.max_depth:
            # Use local import to avoid circular dependency
            from agents.coach_agent import CoachAgent

            coach = CoachAgent(
                self.team_context,
                recursion_depth=self.recursion_depth + 1,
                max_depth=self.max_depth,
            )
            return coach.decide_play(game_state, scenario="special")
        if game_state.get("distance") > 50:
            return "punt"
        return "field_goal"
