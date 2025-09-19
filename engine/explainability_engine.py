"""
Explainability Engine
Produces human-readable rationales for agent actions, with LLM or template fallback.
"""

try:
    import openai
except ImportError:
    openai = None


class ExplainabilityEngine:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        if openai:
            openai.api_key = os.getenv("OPENAI_API_KEY")

    def explain_action(self, state, action, tags=None):
        base = f"Action: {action}. "
        if tags:
            base += "Tags: " + ", ".join(tags) + ". "
        context = f"Game state: {state}"
        prompt = (
            f"As an expert NFL analyst, explain why this action was chosen.\n"
            f"{context}\nAction: {action}\nTags: {tags}\n"
            "Be concise, tactical, and insightful."
        )
        if openai:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You provide expert, transparent NFL explanations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=90,
                temperature=0.5,
            )
            return response.choices[0].message["content"].strip()
        else:
            return (
                base
                + "Reason: The action fits the current down, distance, and strategic context."
            )


# Usage: expl = ExplainabilityEngine(); expl.explain_action(state, action, tags)
"""

class SimulationOrchestrator:
    def __init__(self, state_dim, action_dim):
        self.rl_agent = RLPlayAgent(state_dim, action_dim)
        self.commentary = GenerativeCommentary()
        self.analytics = AdvancedAnalytics()
        self.explainer = ExplainabilityEngine()
        self.state_dim = state_dim
        self.action_dim = action_dim

    def run_simulation(self, initial_state, num_plays=100):
        state = initial_state
        for _ in range(num_plays):
            action = self.rl_agent.select_action(state)
            # Simulate play outcome (replace with real simulation)
            next_state, reward, done, result = self.simulate_play(state, action)
            self.rl_agent.store_transition(state, action, reward, next_state, done)
            self.rl_agent.optimize()
            self.analytics.log_event(state, result)
            comm = self.commentary.generate(result.get("summary", "Play occurred"))
            expl = self.explainer.explain_action(state, action, tags=result.get("tags", []))
            print(f"Play: {result.get('summary', '')}\nCommentary: {comm}\nExplain: {expl}\n")
            if done:
                break
            state = next_state

    def simulate_play(self, state, action):
        # Dummy simulation for demo; replace with full game logic
        next_state = state  # Should be updated
        reward = 1.0 if action % 2 == 0 else 0.0
        done = False
        result = {"summary": f"Action {action} taken.", "tags": ["aggressive" if action % 2 == 0 else "conservative"]}
        return next_state, reward, done, result

# Usage: orchestrator = SimulationOrchestrator(state_dim, action_dim); orchestrator.run_simulation(initial_state)  
"""
