class PossessionMemory:
    """Memory storage for possession-level data."""

    def __init__(self):
        self.memories = []

    def store_memory(self, memory_data):
        """Store a memory."""
        self.memories.append(memory_data)

    def get_memories(self):
        """Get all stored memories."""
        return self.memories


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
