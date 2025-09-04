import json
import os

class StatePersistence:
    def __init__(self, state_path="game_state.json", memory_path="memory_continuity.json"):
        self.state_path = state_path
        self.memory_path = memory_path

    def save_state(self, state):
        with open(self.state_path, 'w') as f:
            json.dump(state, f)

    def load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                return json.load(f)
        return None

    def save_memory(self, memory):
        with open(self.memory_path, 'w') as f:
            json.dump(memory, f)

    def load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        return None
