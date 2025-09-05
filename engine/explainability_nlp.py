import random

class ExplainabilityNLP:
    """
    Generates explanations for agent decisions using tags and templates.
    """
    TEMPLATES = [
        "The agent chose {action} because {reason_1} and {reason_2}.",
        "Due to {reason_1} and {reason_2}, the agent decided to {action}.",
        "{action_cap} was selected considering {reason_1} with {reason_2} as a factor.",
        "Decision: {action}. Influences: {reason_1}, {reason_2}."
    ]
    REASON_MAP = {
        "conversion_rate:3rd_down_high": "a high 3rd down conversion rate",
        "weather:rain": "rainy weather",
        "confidence:high": "high team confidence",
        "qb_under_pressure:composed": "the quarterback's composure under pressure",
        "opponent:defense:zone_blitz": "the opponent's zone blitz defense",
        "moment:heroics": "a heroic moment",
        "down:3": "it was 3rd down",
        "qb_throw_depth:deep": "the quarterback's tendency to throw deep",
        "coaching_tendency:4th_down_aggressive": "an aggressive fourth down coaching tendency",
        # Add more mappings as needed
    }

    def explain(self, action:str, tags:list):
        # Pick up to two mapped reasons, fallback to the raw tag if not mapped
        mapped = [self.REASON_MAP.get(tag, tag.replace("_", " ")) for tag in tags]
        if not mapped:
            mapped = ["general strategy", "game context"]
        selected = (mapped + mapped)[:2]
        template = random.choice(self.TEMPLATES)
        return template.format(
            action=action,
            action_cap=action.capitalize(),
            reason_1=selected[0],
            reason_2=selected[1]
        )