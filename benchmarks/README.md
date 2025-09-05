# Benchmarks Directory

This directory contains scripts and tools for benchmarking the simulation engine's performance and measuring resource usage.

## Intended Use

- **Performance Testing:** Measure the execution time and memory consumption of core simulation loops (e.g., play, drive, game).
- **Regression Detection:** Track changes in performance across code updates.
- **Reproducible Experiments:** Provide harnesses to run simulations with fixed seeds and log results for later analysis.

## Typical Contents

- Benchmark scripts for specific entry points (e.g., `bench_run_play.py`)
- Utility modules for timing and logging
- Output logs and reports (CSV, JSON)

**How to Use:**  
Place benchmarking scripts in this directory. Run them directly or as part of a CI pipeline to monitor performance over time.