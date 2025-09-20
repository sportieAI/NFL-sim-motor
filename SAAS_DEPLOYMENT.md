# SaaS Deployment – Full Stack & API

## Docker/Kubernetes Setup

- **Docker Compose** (for local/dev):
  ```bash
  docker compose up --build
  ```
- **Kubernetes** (for production):
  - See `k8s/` for manifests and Helm charts.
  - Example:
    ```bash
    kubectl apply -f k8s/
    ```

## Prefect Flow Registration

- Register simulation flows for robust orchestration:
  ```bash
  prefect deployment build prefect/flows/simulate.py:simulate \
    -n "NFL Sim Flow" -q default
  prefect deployment apply simulate-deployment.yaml
  ```

## RBAC & API Gateway

- Integrate with your org's RBAC provider.
- Secure endpoints with API gateway (Kong, Traefik, etc.).
- Example: Add API key checks in `api/gateway.py`.

## Multi-Tenant Patterns

- Namespace data and state by organization/client.
- See `/tenancy` for sample code and strategies.
- Use environment variables or config files for tenant isolation.

## Monitoring & Signal Health

- Built-in hooks for metrics and alerts.
- Integrate with Prometheus, Datadog, or your preferred stack.
- All simulation events are logged; see `/logs` for audit trail.
