"""
Unit tests for memory continuity module.
"""
import unittest
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory_continuity import MemoryContinuity  # Import the actual class


class TestMemoryContinuity(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryContinuity()

    def test_memory_initialization(self):
        """Test that memory initializes correctly."""
        self.assertEqual(len(self.memory.memory), 0)

    def test_memory_update(self):
        """Test that memory updates correctly."""
        possession_state = {"down": 1, "distance": 10}
        outcome = {"yards": 5}
        tags = ["run", "successful"]
        
        self.memory.update(possession_state, outcome, tags)
        
        self.assertEqual(len(self.memory.memory), 1)
        self.assertIn("possession_state", self.memory.memory[0])
        self.assertIn("outcome", self.memory.memory[0])
        self.assertIn("tags", self.memory.memory[0])


if __name__ == '__main__':
    unittest.main()