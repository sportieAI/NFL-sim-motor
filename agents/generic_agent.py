from engine.tagging_engine import TaggingEngine
from engine.explainability_nlp import ExplainabilityNLP

class GenericAgent:
    def __init__(self, name="Agent"):
        self.name = name
        self.tagger = TaggingEngine()
        self.explainer = ExplainabilityNLP()
        self.last_action = None
        self.last_tags = []

    def decide(self, state:dict):
        # Example: Decision logic (replace with actual model or rules)
        if state.get("down") == "3" and state.get("distance") == "long":
            action = "pass_deep"
        elif state.get("weather") == "rain":
            action = "run_inside"
        else:
            action = "pass_short"
        self.last_action = action
        self.last_tags = self.tagger.tag_decision(state)
        return action

    def get_explanation(self):
        return self.explainer.explain(self.last_action, self.last_tags)