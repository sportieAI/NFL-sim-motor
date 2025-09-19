from collections import deque
from typing import List, Dict, Any

ARC_PHASES = ["setup", "rising_action", "climax", "falling_action", "resolution"]


class NarrativeEvent:
    def __init__(self, event: Dict[str, Any]):
        self.timestamp = event.get("timestamp", datetime.utcnow().isoformat())
        self.entity = event.get("entity")
        self.event_type = event.get("event")
        self.outcome = event.get("outcome")
        self.score_delta = event.get("score_delta", 0)
        self.tags = event.get("tags", [])
        self.raw = event


class NarrativeTracker:
    """
    Tracks storyline, arc phase, tension, and highlights for a single agent or team.
    """

    def __init__(self, entity_id: str):
        self.entity = entity_id
        self.events: List[NarrativeEvent] = []
        self.tension = 0
        self.phase = ARC_PHASES[0]
        self.peaks: List[Dict[str, Any]] = []
        self.turning_points: List[Dict[str, Any]] = []
        self.last_score = 0

    def update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        nev = NarrativeEvent(event)
        self.events.append(nev)
        # Update tension (e.g., based on score change, outcome, custom logic)
        self.tension += abs(nev.score_delta)
        event["tension"] = self.tension

        # Arc phase logic
        if nev.event_type in ["touchdown", "big_play"]:
            self.phase = "rising_action"
        if nev.event_type in ["clutch", "game_winning"]:
            self.phase = "climax"
            self.peaks.append(event)
        if nev.event_type in ["turnover", "collapse"]:
            self.phase = "falling_action"
            self.turning_points.append(event)
        if nev.event_type in ["kneel_down", "timeout_end"]:
            self.phase = "resolution"
        event["arc_phase"] = self.phase

        # Highlight reel (pivotal moments)
        if "highlight" in nev.tags or nev.event_type in [
            "clutch",
            "turnover",
            "big_play",
        ]:
            event["highlight_reel"] = True
        else:
            event["highlight_reel"] = False

        # Narrative headline
        event["headline"] = self.generate_headline(event)
        return event

    def generate_headline(self, event):
        # Simple headline logic; extend with more narrative flavor!
        if event["arc_phase"] == "climax":
            return f"{event['entity']} delivers in the clutch!"
        elif event["arc_phase"] == "falling_action":
            return f"Momentum shifts after {event['event']}"
        elif event["arc_phase"] == "rising_action":
            return f"{event['entity']} builds momentum"
        elif event["arc_phase"] == "resolution":
            return f"Game resolves for {event['entity']}"
        else:
            return f"{event['entity']} {event['event']}"

    def summarize(self) -> str:
        # Summarize narrative arc for dashboards, recaps, or LLM input
        summary = []
        for event in self.events:
            summary.append(
                event.raw.get("headline", f"{event.entity} {event.event_type}")
            )
        return " | ".join(summary)

    def highlight_reel(self) -> List[Dict[str, Any]]:
        return [evt.raw for evt in self.events if getattr(evt, "highlight_reel", False)]


# --------- Multi-Agent/Team Narrative ---------


class MultiAgentNarrativeEngine:
    """
    Orchestrates narrative tracking for multiple entities, supports cross-entity drama.
    """

    def __init__(self):
        self.agents: Dict[str, NarrativeTracker] = {}

    def update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        entity = event.get("entity")
        if entity not in self.agents:
            self.agents[entity] = NarrativeTracker(entity)
        return self.agents[entity].update(event)

    def full_narrative_summary(self) -> str:
        # Combine all trackers' summaries for LLM or dashboard use
        return "\n".join([tracker.summarize() for tracker in self.agents.values()])

    def highlight_reels(self) -> Dict[str, List[Dict[str, Any]]]:
        return {eid: tracker.highlight_reel() for eid, tracker in self.agents.items()}


# --------- LLM Narration Integration (stub) ---------


def generate_llm_narrative(summary: str) -> str:
    """
    Plug in your LLM of choice (OpenAI, HuggingFace, etc.)
    """
    # Example stub; replace with actual LLM call
    return f"Narrator: {summary}"


# --------- Example usage in simulation ---------

if __name__ == "__main__":
    engine = MultiAgentNarrativeEngine()
    # Simulate event stream
    events = [
        {
            "timestamp": "2025-09-05T01:00:00",
            "entity": "QB_17",
            "event": "snap",
            "outcome": "success",
            "score_delta": 0,
        },
        {
            "timestamp": "2025-09-05T01:00:05",
            "entity": "QB_17",
            "event": "big_play",
            "outcome": "complete",
            "score_delta": 40,
            "tags": ["highlight"],
        },
        {
            "timestamp": "2025-09-05T01:00:10",
            "entity": "QB_17",
            "event": "clutch",
            "outcome": "touchdown",
            "score_delta": 7,
            "tags": ["highlight"],
        },
        {
            "timestamp": "2025-09-05T01:00:15",
            "entity": "QB_17",
            "event": "kneel_down",
            "outcome": "success",
            "score_delta": 0,
        },
        {
            "timestamp": "2025-09-05T01:01:00",
            "entity": "LB_52",
            "event": "turnover",
            "outcome": "fumble_recovery",
            "score_delta": 0,
            "tags": ["highlight"],
        },
    ]
    for evt in events:
        enriched_evt = engine.update(evt)
        print(enriched_evt["headline"])
    # Generate a storyline
    summary = engine.full_narrative_summary()
    # Get LLM narration
    narration = generate_llm_narrative(summary)
    print(narration)
