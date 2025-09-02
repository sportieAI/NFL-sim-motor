class Agent:
    """
    Basic agent for simulation.
    Customize with specific logic for your simulation needs.
    """

    def __init__(self, name, state=None):
        self.name = name
        self.state = state if state is not None else {}

    def act(self, environment):
        """
        Define agent's action logic.
        """
        # Example: Take a random action or implement policy
        action = None
        # TODO: Add agent action logic
        return action

    def update_state(self, new_state):
        """
        Update the agent's internal state.
        """
        self.state = new_state

    def __repr__(self):
        return f"<Agent name={self.name}, state={self.state}>"
