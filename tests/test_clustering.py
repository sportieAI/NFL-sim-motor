"""
Unit tests for clustering module.
"""

import unittest
from clustering import PlayClusterer  # adjust import as needed


class TestPlayClusterer(unittest.TestCase):
    def setUp(self):
        self.clusterer = PlayClusterer()
        self.data = [
            {"play": "pass complete", "yards": 8},
            {"play": "run left", "yards": 4},
            {"play": "pass incomplete", "yards": 0},
        ]

    def test_cluster(self):
        clusters = self.clusterer.cluster(self.data)
        self.assertIsInstance(clusters, dict)
        self.assertTrue(len(clusters) > 0)


if __name__ == "__main__":
    unittest.main()
