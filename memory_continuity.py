class MemoryContinuity:
    """
    Maintains continuity of possession-level trends, momentum, and emotion.
    """

    def __init__(self):
        self.memory = []

    def update(self, possession_state, outcome, tags):
        self.memory.append(
            {
                "possession_state": possession_state.copy(),
                "outcome": outcome.copy(),
                "tags": tags[:],
            }
        )


memory_continuity = MemoryContinuity()
