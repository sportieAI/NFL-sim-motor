# 🚀 Benchmarking & Evaluation Guide

This document explains how to run performance benchmarks for the project.

---

## 1. Running All Benchmarks

To execute all available benchmark tests, use:

```bash
python benchmarks/run_all.py
```

This script will automatically discover and run all performance and evaluation tests in the `benchmarks/` directory.

---

## 2. Benchmark Output

- Results are printed to the console.
- Some benchmarks may also output results to files (e.g., `benchmark_results.json` or `.csv` in the `benchmarks/results/` directory).

---

## 3. Custom Benchmark Runs

You can run specific benchmark scripts directly. For example:

```bash
python benchmarks/benchmark_simulation.py --scenario "KC_vs_SF" --season 2023
```

Check inside each script or run with `--help` for available arguments.

---

## 4. Interpreting Results

Typical metrics include:
- **Throughput**: Events or simulations per second.
- **Latency**: Time per event or simulation.
- **Resource Usage**: CPU and memory footprint.
- **Error Rate**: Number of failures or exceptions.

---

## 5. Visualizing Results (Optional)

For advanced analysis, results can be loaded into a notebook or visualization tool:

```python
import pandas as pd
df = pd.read_json('benchmarks/results/benchmark_results.json')
df.plot(x='scenario', y='latency_ms', kind='bar')
```

---

## 6. Tips

- Ensure you have all required dependencies:  
  ```bash
  pip install -r benchmarks/requirements.txt
  ```
- For repeatable results, use the same hardware and seed values.
- Review and contribute new benchmark scripts to the `benchmarks/` directory.

---

For questions or contributions, please open an issue or PR!