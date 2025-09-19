# NFL Simulation Engine: Sports Intelligence Stack

This repository contains a modular NFL simulation engine with advanced sports intelligence capabilities. It supports real-time and historical data ingestion, meta-learning, explainable AI, and emotional modeling for next-generation sports analytics and simulation.

---

## 🏈 External Data Sources for Sports Intelligence

| **Source Type**            | **Examples / APIs**                               | **Use Case**                                               |
|----------------------------|---------------------------------------------------|------------------------------------------------------------|
| Game Stats & Play-by-Play  | Sportradar, Stats Perform, ESPN API               | Real-time feeds, possession-level stats, player actions    |
| Fantasy & Projections      | FantasyData, Sleeper API                          | Emotional resonance modeling, predictive overlays          |
| Betting & Odds             | OddsAPI, Betfair                                  | Market sentiment, strategic cognition, volatility tagging  |
| Injury Reports & Contracts | ProFootballFocus, Spotrac                         | Signal integrity, player availability, emotional triggers  |
| Historical Archives        | Pro-Football-Reference, Kaggle datasets           | Benchmarking, clustering, causal inference                 |

---

## 🧩 Libraries for Simulation, Cognition & Explainability

| **Category**           | **Libraries**                                           | **Description / Use Case**                     |
|------------------------|--------------------------------------------------------|------------------------------------------------|
| Simulation & Modeling  | `simpy`, `mesa`, `PyGame`                              | Discrete-event simulation, agent-based models, visual game/theater |
| Causal Inference       | `DoWhy`, `CausalML`, `econml`                          | Causal modeling, treatment effect estimation   |
| Clustering & Tagging   | `scikit-learn`, `hdbscan`, `spaCy`                     | ML clustering, density estimation, NLP tagging |
| Explainable AI         | `SHAP`, `LIME`, `Captum`                               | Model interpretability and explainable AI      |
| Emotional Feedback     | `pyaudio`, `librosa`, `torchcrepe`                     | Audio/music/voice synthesis & analysis         |
| Persistence & Memory   | `pickle`, `joblib`, `SQLite`, `Firebase`, `Supabase`, `Redis` | Serialization, local & cloud storage, fast memory, scalable state  |

---

## 📊 Apps & Platforms for Stats & Visualization

| **App / Platform**     | **Use Case**                                           |
|------------------------|--------------------------------------------------------|
| Tableau / Power BI     | Visualizing simulation outcomes & emotional overlays   |
| Notion / Obsidian      | Milestone tracking, memory continuity logs             |
| GitHub + Codespaces    | Modular builds, CI/CD, version control                 |
| JupyterLab             | Interactive debugging, explainability dashboards       |

---

## 🚦 Integration Pattern

- **Data flows from external APIs/files** into `ingest` modules.
- **Simulation engine** (see `engine/` and `agent/`) controls play-by-play logic and state.
- **Causal, clustering, and explainability modules** analyze and explain outcomes.
- **Persistence** is handled via local (`pickle`, `SQLite`) or cloud (`Firebase`, `Supabase`, `Redis`) stores.
- **Visualization and dashboards** are externalized to Tableau, Power BI, or Jupyter.

---

## 🛠️ Example: Ingesting and Using External Data

```python
from data.ingest_game_data import ingest_team_data, ingest_player_stats

team_stats = ingest_team_data(team_id="NE", season_year=2024)
player_stats = ingest_player_stats(player_id="1234", season_year=2024)
```

---

## 📦 Quickstart

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run simulation:
   ```sh
   python main.py
   ```
3. Analyze results in JupyterLab or export to Tableau/Power BI.

---

## 🔐 Security & Documentation

- **[Security Policy](SECURITY.md)**: Secret management, key rotation, and security best practices
- **[Changelog](CHANGELOG.md)**: Data contract changes and schema evolution history
- **[Schema Validation](tests/test_validate_schemas.py)**: Test script for JSON schema validation

### Secret Management
All sensitive configuration should use environment variables:
```bash
export REDIS_URL="redis://localhost:6379/0"
export POSTGRES_URL="postgresql://localhost:5432/nfl_sim"
export NFL_API_KEY="your_api_key_here"
```

---

## 📊 Observability & Monitoring

### Structured Logging
The engine uses structured JSON logging with correlation IDs for traceability:

```python
# Example structured log entry
{
  "timestamp": "2025-01-21T10:30:00Z",
  "level": "INFO",
  "service": "simulation_engine",
  "correlation_id": "poss_12345_snap_67",
  "event": "play_executed",
  "play_type": "pass_short",
  "yards_gained": 8,
  "success": true,
  "metrics": {
    "execution_time_ms": 45,
    "tags_applied": 3
  }
}
```

### Key Metrics

#### Performance Metrics
- **Latency**: p50/p95 execution time per snap
- **Throughput**: Simulations per second
- **Error Rate**: Failed simulations / total simulations
- **Queue Depth**: Pending simulation requests

#### Business Metrics  
- **Tag Coverage**: Percentage of plays with ontological tags
- **Cluster Stability**: Consistency of play clustering over time
- **Narrative Quality**: Coherence scores for generated commentary
- **Memory Continuity**: Long-term state preservation accuracy

### Log Configuration
Configure logging levels by environment:
```yaml
# staging.yaml
logging:
  level: DEBUG
  structured: true
  correlation_ids: true
  console_output: true

# prod.yaml  
logging:
  level: INFO
  structured: true
  correlation_ids: true
  console_output: false
  file_output: "/var/log/nfl-sim/app.log"
```

### OpenTelemetry Tracing
The `simulate_play` pipeline is instrumented with OpenTelemetry traces:
- Span per play execution
- Context propagation across service boundaries
- Custom attributes for play metadata
- Integration with Jaeger/Zipkin for trace visualization

### Monitoring Endpoints
- **Health Check**: `GET /health` - Service health status
- **Metrics**: `GET /metrics` - Prometheus-compatible metrics
- **Ready Check**: `GET /ready` - Readiness for traffic

---

## 📝 References

- See `docs/` for coverage, CI, and API documentation.
- See `data/` and `engine/` for module implementations.

---

**Built for modular extension — plug in new data sources, AI models, or visualization tools as needed!**