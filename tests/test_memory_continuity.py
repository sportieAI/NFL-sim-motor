"""
Unit tests for memory continuity module.
"""
import unittest
from memory_continuity import MemoryContinuity  # adjust import as needed

class TestMemoryContinuity(unittest.TestCase):
    def test_memory_tracking(self):
        memory = MemoryContinuity()
        state = {"down": 1, "distance": 10}
        outcome = {"yards": 5, "success": True}
        tags = ["aggressive", "passing"]
        
        memory.update(state, outcome, tags)
        
        self.assertEqual(len(memory.memory), 1)
        self.assertEqual(memory.memory[0]["possession_state"]["down"], 1)
        self.assertEqual(memory.memory[0]["outcome"]["yards"], 5)

if __name__ == '__main__':
    unittest.main()