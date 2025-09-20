"""
Unit tests for clustering module.
"""

import unittest
from clustering import cluster_play  # adjust import as needed


class TestPlayClustering(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"play": "pass complete", "yards": 8},
            {"play": "run left", "yards": 4},
            {"play": "pass incomplete", "yards": 0},
        ]

    def test_cluster_play(self):
        # Test the cluster_play function
        play_call = {"play": "pass complete", "yards": 8}
        outcome = {"result": "success", "points": 0}
        cluster_id = cluster_play(play_call, outcome)
        self.assertIsInstance(cluster_id, int)
        self.assertTrue(0 <= cluster_id < 10)


if __name__ == "__main__":
    unittest.main()
