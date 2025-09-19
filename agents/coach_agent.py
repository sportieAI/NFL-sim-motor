from agents.play_calling_agent import PlayCallingAgent
from agents.defensive_agent import DefensiveAgent
from agents.special_teams_agent import SpecialTeamsAgent


class CoachAgent:
    def __init__(self, team_context, recursion_depth=0, max_depth=3):
        self.team_context = team_context
        self.recursion_depth = recursion_depth
        self.max_depth = max_depth

    def decide_play(self, game_state, scenario):
        if self.recursion_depth >= self.max_depth:
            return "default_play"

        if scenario == "critical":
            play_agent = PlayCallingAgent(
                self.team_context,
                recursion_depth=self.recursion_depth + 1,
                max_depth=self.max_depth,
            )
            return play_agent.suggest_play(game_state)
        elif scenario == "defense":
            def_agent = DefensiveAgent(
                self.team_context,
                recursion_depth=self.recursion_depth + 1,
                max_depth=self.max_depth,
            )
            return def_agent.choose_defense(game_state)
        elif scenario == "special":
            st_agent = SpecialTeamsAgent(
                self.team_context,
                recursion_depth=self.recursion_depth + 1,
                max_depth=self.max_depth,
            )
            return st_agent.select_special_teams_play(game_state)
        else:
            return self._standard_play(game_state)

    def _standard_play(self, game_state):
        return "run" if game_state.get("down") == 1 else "pass"
