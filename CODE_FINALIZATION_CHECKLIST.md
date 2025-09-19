# Code Finalization Checklist for Go-Live

## Configuration and Secrets
- [ ] `staging.yaml` and `prod.yaml` exist, with toggles for randomness, logging, endpoints
- [ ] No secrets in codebase (managed via environment variables or vault)
- [ ] Documented key rotation and secret management process
- [ ] Automated scans for secrets in code (e.g., TruffleHog, GitHub Advanced Security)

## Data Contracts
- [ ] JSONSchema defined for `PlayEvent`, `DriveSnapshot`, `Narrative`, `TagBundle`
- [ ] Schemas validated in CI tests
- [ ] Data contract versioning uses SemVer
- [ ] Compatibility tests for schema upgrades
- [ ] Upgrade notes in CHANGELOG or docs

## Observability
- [ ] Structured JSON logging (with correlation IDs per possession)
- [ ] Log level settable by environment
- [ ] Metrics: p50/p95 latency per snap, error rate, queue depth, tag coverage, cluster stability
- [ ] OpenTelemetry traces instrument `simulate_play` pipeline

## Storage
- [ ] Redis integration for recent possessions and rolling features (hot store)
- [ ] Postgres/Supabase for events, tags, metrics (cold store)
- [ ] S3-compatible storage for raw feeds, parquet snapshots, model artifacts (blob)
- [ ] pgvector/FAISS for scenario recall (vector store)

## Reliability
- [ ] Ingest → simulate → emit decoupled by broker (Redis Streams, RabbitMQ, Pub/Sub)
- [ ] Deterministic event keys and replay-safe, idempotent consumers
- [ ] Exponential backoff and Dead Letter Queue (DLQ) for retries

## Security
- [ ] All APIs require signed requests
- [ ] Rate limiting for ingest endpoints
- [ ] IP allowlist for admin interfaces
- [ ] Honeypot endpoints with telemetry routed to separate project

## CI/CD
- [ ] CI pipeline: lint, mypy, unit, property-based, and integration tests
- [ ] Docker images built and tagged per commit
- [ ] Staging deploys run smoke tests before progressive prod rollout (canary)

---

_Last updated: 2025-09-19_