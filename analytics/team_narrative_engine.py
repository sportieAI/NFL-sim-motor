from collections import deque
from typing import List, Dict, Any

ARC_PHASES = ["setup", "rising_action", "climax", "falling_action", "resolution"]


class TeamArc:
    def __init__(self, team_id: str, rival_id: Optional[str] = None):
        self.team_id = team_id
        self.rival_id = rival_id
        self.events: List[Dict[str, Any]] = []
        self.phase = ARC_PHASES[0]
        self.tension = 0
        self.momentum = 0
        self.headlines: List[str] = []
        self.turning_points: List[Dict[str, Any]] = []
        self.peaks: List[Dict[str, Any]] = []
        self.score = 0
        self.rival_score = 0

    def update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        self.events.append(event)
        # Score and momentum logic
        self.score += event.get("score_delta", 0)
        if self.rival_id and "rival_score_delta" in event:
            self.rival_score += event["rival_score_delta"]
        self.momentum += event.get("momentum_delta", 0)
        self.tension += abs(event.get("score_delta", 0))

        # Arc phase logic
        if event.get("event") in ["big_play", "lead_change"]:
            self.phase = "rising_action"
        if event.get("event") in ["comeback", "clutch", "game_winner"]:
            self.phase = "climax"
            self.peaks.append(event)
        if event.get("event") in ["turnover", "collapse"]:
            self.phase = "falling_action"
            self.turning_points.append(event)
        if event.get("event") in ["kneel_down", "final_whistle"]:
            self.phase = "resolution"

        event["arc_phase"] = self.phase
        event["team_score"] = self.score
        event["team_momentum"] = self.momentum
        event["tension"] = self.tension

        # Rival logic
        if self.rival_id:
            margin = self.score - self.rival_score
            event["rivalry_margin"] = margin
            if abs(margin) <= 3 and self.phase == "climax":
                event["rivalry_peak"] = True

        # Headline
        headline = self.generate_headline(event)
        event["headline"] = headline
        self.headlines.append(headline)
        return event

    def generate_headline(self, event):
        if event.get("arc_phase") == "climax":
            if event.get("rivalry_peak"):
                return f"Rivalry heats up: {self.team_id} and {self.rival_id} neck and neck!"
            return f"{self.team_id} delivers in the clutch!"
        elif event.get("arc_phase") == "falling_action":
            return f"{self.team_id} faces setback after {event.get('event')}"
        elif event.get("arc_phase") == "rising_action":
            return f"{self.team_id} surges ahead"
        elif event.get("arc_phase") == "resolution":
            return f"Final whistle: {self.team_id} {self.score} - {self.rival_id} {self.rival_score}"
        else:
            return f"{self.team_id} {event.get('event')}"

    def storyline(self):
        return " | ".join(self.headlines)

    def highlight_reel(self):
        return [
            evt
            for evt in self.events
            if evt.get("arc_phase") in ["climax", "falling_action"]
            or evt.get("rivalry_peak")
        ]


class TeamNarrativeEngine:
    """
    Tracks arcs for each team and rivalry, supports full-game and rivalry analytics.
    """

    def __init__(self):
        self.teams: Dict[str, TeamArc] = {}
        self.rivalries: List[tuple] = []

    def add_rivalry(self, team1: str, team2: str):
        self.rivalries.append((team1, team2))
        if team1 not in self.teams:
            self.teams[team1] = TeamArc(team1, team2)
        else:
            self.teams[team1].rival_id = team2
        if team2 not in self.teams:
            self.teams[team2] = TeamArc(team2, team1)
        else:
            self.teams[team2].rival_id = team1

    def update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        team = event.get("team")
        if team not in self.teams:
            self.teams[team] = TeamArc(team)
        return self.teams[team].update(event)

    def full_game_storyline(self):
        return "\n".join([arc.storyline() for arc in self.teams.values()])

    def rivalry_highlights(self):
        highlights = {}
        for team1, team2 in self.rivalries:
            arc1 = self.teams.get(team1)
            arc2 = self.teams.get(team2)
            if arc1 and arc2:
                highlights[(team1, team2)] = (
                    arc1.highlight_reel() + arc2.highlight_reel()
                )
        return highlights

    def rivalry_summary(self, team1: str, team2: str):
        arc1 = self.teams.get(team1)
        arc2 = self.teams.get(team2)
        if not arc1 or not arc2:
            return f"No rivalry data between {team1} and {team2}."
        margin = arc1.score - arc2.score
        if margin == 0:
            verdict = "draw"
        elif margin > 0:
            verdict = f"{team1} wins by {margin}"
        else:
            verdict = f"{team2} wins by {-margin}"
        return f"{team1} ({arc1.score}) vs {team2} ({arc2.score}): {verdict}"


# Example usage:
if __name__ == "__main__":
    engine = TeamNarrativeEngine()
    engine.add_rivalry("Lions", "Bears")
    events = [
        {
            "timestamp": "2025-09-05T01:00:00",
            "team": "Lions",
            "event": "snap",
            "score_delta": 0,
        },
        {
            "timestamp": "2025-09-05T01:00:01",
            "team": "Bears",
            "event": "turnover",
            "score_delta": 0,
        },
        {
            "timestamp": "2025-09-05T01:00:05",
            "team": "Lions",
            "event": "big_play",
            "score_delta": 40,
            "momentum_delta": 2,
        },
        {
            "timestamp": "2025-09-05T01:00:10",
            "team": "Bears",
            "event": "comeback",
            "score_delta": 7,
            "momentum_delta": 3,
        },
        {
            "timestamp": "2025-09-05T01:00:15",
            "team": "Lions",
            "event": "lead_change",
            "score_delta": 7,
        },
        {
            "timestamp": "2025-09-05T01:00:20",
            "team": "Lions",
            "event": "game_winner",
            "score_delta": 3,
        },
        {
            "timestamp": "2025-09-05T01:00:25",
            "team": "Bears",
            "event": "final_whistle",
            "score_delta": 0,
        },
    ]
    # Simulate rivalry score deltas
    for evt in events:
        if evt["team"] == "Lions":
            evt["rival_score_delta"] = next(
                (
                    e["score_delta"]
                    for e in events
                    if e.get("team") == "Bears"
                    and e.get("timestamp") == evt["timestamp"]
                ),
                0,
            )
        elif evt["team"] == "Bears":
            evt["rival_score_delta"] = next(
                (
                    e["score_delta"]
                    for e in events
                    if e.get("team") == "Lions"
                    and e.get("timestamp") == evt["timestamp"]
                ),
                0,
            )
        engine.update(evt)

    print(engine.full_game_storyline())
    print(engine.rivalry_summary("Lions", "Bears"))
    print(engine.rivalry_highlights())
