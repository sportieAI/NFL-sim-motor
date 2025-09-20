"""
Performance benchmarking utilities.
"""

import time

def run_benchmark(simulator, test_data, repeat=100):
    """
    Benchmark simulation performance.
    Args:
        simulator (NFLSimulator): Simulator instance.
        test_data (dict): Example play data.
        repeat (int): Number of repetitions.
    Returns:
        dict: Benchmark metrics.
    """
    start = time.time()
    for _ in range(repeat):
        simulator.simulate_play(test_data)
    elapsed = time.time() - start
    return {"runs": repeat, "total_seconds": elapsed, "per_sim_seconds": elapsed / repeat}