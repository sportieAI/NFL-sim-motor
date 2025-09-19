"""
Unit tests for clustering module.
"""
import unittest
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from clustering import cluster_play  # Import the actual function


class TestPlayClustering(unittest.TestCase):
    def test_cluster_play_basic(self):
        """Test basic clustering functionality."""
        play_call = {"type": "run", "direction": "left"}
        outcome = {"yards": 5, "success": True}
        
        # Test that function returns an integer cluster ID
        cluster_id = cluster_play(play_call, outcome)
        self.assertIsInstance(cluster_id, int)
        self.assertGreaterEqual(cluster_id, 0)
        self.assertLess(cluster_id, 10)  # Based on modulo 10 in implementation

    def test_cluster_play_consistency(self):
        """Test that same play calls get same cluster ID."""
        play_call = {"type": "pass", "distance": "short"}
        outcome = {"yards": 3, "success": True}
        
        cluster_id1 = cluster_play(play_call, outcome)
        cluster_id2 = cluster_play(play_call, outcome)
        
        self.assertEqual(cluster_id1, cluster_id2)


if __name__ == '__main__':
    unittest.main()
