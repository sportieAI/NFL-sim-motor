class LLMNarrator:
    """LLM-based narrator with prompt guardrails. Swap in OpenAI/LLM API as needed."""

    def __init__(self, llm_client=None):
        # llm_client: Any object with .generate(prompt)
        self.llm = llm_client

    def narrate(self, play, cluster, prediction):
        base_prompt = (
            f"Team: {play.get('team', 'Team')}\n"
            f"Description: {play.get('description', 'No description')}\n"
            f"Cluster: {cluster}\n"
            f"Prediction: {prediction}\n"
            "Write a vivid, factual, and emotionally resonant one-sentence NFL play summary. "
            "Do not speculate or include inappropriate content."
        )
        if self.llm is None:
            # Fallback to template
            return (
                f"{play.get('team', 'Team')}: {play.get('description', 'No description')} "
                f"(Cluster: {cluster}) | Predicted: {prediction.get('expected_yards', 0):.1f} yards"
            )
        # Implement safety/guardrails here as needed
        return self.llm.generate(base_prompt)