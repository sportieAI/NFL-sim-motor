# Simulation Guide

## Historical Replay

- Run past seasons/games with real data:
  ```bash
  python dashboard_and_api.py --replay data/2023_week_1.json
  ```

## Agent-Based Simulation

- Add your agent logic to `/agents/`.
- Configure agent selection in your simulation config.
- Example:
  ```bash
  python dashboard_and_api.py --agent my_agent.py
  ```

## Firehose Ingestion

- Ingest live or bulk data for continuous simulation:
  ```bash
  python ingest.py --source live
  ```

## Benchmarking

- Compare agent performance and simulation fidelity.
- Use `/benchmarks` for ready-made scripts.

## Post-Simulation Hooks

- Trigger analytics, narration, export, or webhooks after each run.
- Example: Add your script to `/post_hooks/` and register in config.

---

## 🧬 Optional Add-ons

- LLM-based commentary and voice modules (see [EXTENSIONS.md](./EXTENSIONS.md))
- Security & signal integrity (see [SECURITY.md](./SECURITY.md))
- API integration (see [API_REFERENCE.md](./API_REFERENCE.md))