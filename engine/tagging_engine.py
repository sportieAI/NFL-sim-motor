from ontology.tagging_ontology import all_tags

class TaggingEngine:
    """
    Simple rule-based tagging engine.
    In a real system, this could be NLP-driven or ML-enhanced.
    For now, it matches against state dict keys and values.
    """
    def __init__(self):
        self.known_tags = set(all_tags())

    def tag_decision(self, state: dict) -> list:
        tags = []
        # Scan state and match tags based on heuristic rules
        for key, value in state.items():
            if isinstance(value, str):
                candidate = f"{key}:{value}"
                if candidate in self.known_tags:
                    tags.append(candidate)
        # Example: Add contextual tags
        if 'down' in state and state['down'] == '3' and state.get('conversion_rate', '') == 'high':
            tags.append("conversion_rate:3rd_down_high")
        if state.get('weather') == 'rain':
            tags.append("weather:rain")
        # Add more logic as needed for your simulation
        return tags
