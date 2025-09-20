import os
import json
from datetime import datetime

class MemoryManager:
    """JSONL file-based episodic memory store."""

    def __init__(self, memory_dir="memory_store"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)

    def update(self, play, tags, cluster):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        filename = os.path.join(self.memory_dir, f"{today}.jsonl")
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "play": play,
            "tags": tags,
            "cluster": cluster
        }
        with open(filename, "a") as f:
            f.write(json.dumps(snapshot) + "\n")
        return snapshot

    def recall(self, date=None):
        # Returns all memories for the given date
        date = date or datetime.utcnow().strftime("%Y-%m-%d")
        filename = os.path.join(self.memory_dir, f"{date}.jsonl")
        if not os.path.exists(filename):
            return []
        with open(filename, "r") as f:
            return [json.loads(line) for line in f]
