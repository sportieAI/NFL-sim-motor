import time
import importlib
import sys


def run_play_simulation(sim_module="simulation", entry_func="run_play", iterations=100):
    """
    Benchmarks the play simulation loop.

    Args:
        sim_module (str): The simulation module to import.
        entry_func (str): The function to call for a single play simulation.
        iterations (int): Number of iterations to run.

    Returns:
        float: Total elapsed time in seconds.
    """
    try:
        sim = importlib.import_module(sim_module)
        func = getattr(sim, entry_func)
    except (ImportError, AttributeError) as e:
        print(f"Could not import {sim_module}.{entry_func}: {e}")
        sys.exit(1)

    start = time.perf_counter()
    for _ in range(iterations):
        func()
    end = time.perf_counter()
    elapsed = end - start
    print(
        f"Executed {iterations} iterations in {elapsed:.4f} seconds ({elapsed/iterations:.6f} per iteration)"
    )
    return elapsed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark the play simulation loop.")
    parser.add_argument(
        "--sim-module", type=str, default="simulation", help="Simulation module name"
    )
    parser.add_argument(
        "--entry-func", type=str, default="run_play", help="Entry function name"
    )
    parser.add_argument(
        "--iterations", type=int, default=100, help="Number of iterations"
    )
    args = parser.parse_args()
    run_play_simulation(args.sim_module, args.entry_func, args.iterations)
