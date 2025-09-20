# 📡 Data Collection & Feedback Pipeline

## Real-Time or Historical Data Ingestion

Run the following command to start ingesting live or historical data:

```bash
python data_collection/firehose_to_feedback.py --mode=real_time
```

---

## Pipeline Steps

1. **Ingest Live or Historical Data**  
   The script connects to your data source and continuously ingests incoming (or historical) events.

2. **Tag, Cluster, and Route Events**  
   Events are automatically tagged and clustered. The system routes them to appropriate downstream components.

3. **Trigger Simulation Loop**  
   As relevant events are processed, the simulation loop is triggered, allowing for near real-time or backtest simulations.

4. **Persist Enriched Outputs**  
   All enriched and processed outputs are persisted to your configured storage/database for analysis and further use.

---

**Tip:**  
- Ensure your `.env` file is properly configured for data sources and output persistence.
- For historical ingestion, adjust the `--mode` flag as appropriate (e.g., `--mode=historical`).

---

## 🧠 5. Orchestration (Optional)
Use Prefect for multi-tenant orchestration.

### Prefect Orchestration Quickstart

```bash
prefect server start
prefect deployment build flows/sim_orchestrator.py:SimFlow -n "NFL-Sim"
prefect deployment apply SimFlow-deployment.yaml
prefect agent start
```

- Make sure you have Prefect installed (`pip install prefect`).
- Visit `http://localhost:4200` to access the Prefect UI.
- Adjust deployment and flow names as needed for your pipeline.

For further details, see [Prefect documentation](https://docs.prefect.io/).