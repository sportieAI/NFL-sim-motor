# Advanced API Patterns: REST, GraphQL, and WebSocket

A collection of best practices and advanced patterns for building robust, scalable APIs using REST, GraphQL, and WebSockets in a SaaS or simulation context.

---

## 1. REST API Patterns

### a. Resource-Oriented Design
- Use nouns for endpoints (`/simulations`, `/users/{id}`).
- Nest resources for relationships (`/users/{id}/simulations`).

### b. Idempotent Operations
- Use proper HTTP verbs: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`.
- Support idempotency keys for POST requests (`Idempotency-Key` header).

### c. Pagination, Filtering, Sorting
- Implement cursor-based pagination: `GET /simulations?after=abc123&limit=20`.
- Allow filtering and sorting via query parameters.

### d. Versioning
- Use media-type versioning (`Accept: application/vnd.api+json;version=2`) or URI versioning (`/v2/simulations`).

### e. HATEOAS
- Include hypermedia links in responses for discoverability.

```json
{
  "id": "sim-123",
  "status": "running",
  "links": [
    { "rel": "self", "href": "/simulations/sim-123" },
    { "rel": "results", "href": "/simulations/sim-123/results" }
  ]
}
```

---

## 2. GraphQL API Patterns

### a. Schema Design
- Modularize schema by domain (`simulation`, `user`, `analytics`).
- Use interfaces and unions for polymorphic types.

### b. Query Optimization
- Use DataLoader pattern to batch and cache DB calls.
- Implement query complexity analysis and depth limiting to avoid over-fetching.

### c. Authorization & Context
- Pass tenant/user info in context.
- Use field-level authorization via custom directives.

```graphql
directive @auth(role: String) on FIELD_DEFINITION

type Simulation {
  id: ID!
  sensitiveField: String @auth(role: "admin")
}
```

### d. Subscriptions
- Use for real-time updates (e.g., simulation status).
- Implement with WebSockets or server-sent events.

```graphql
subscription OnSimulationStatus($id: ID!) {
  simulationStatusChanged(simulationId: $id) {
    id
    status
    progress
  }
}
}
```

---

## 3. WebSocket API Patterns

### a. Connection Lifecycle
- Authenticate on connect (JWT or API key).
- Implement ping/pong keepalives.

### b. Channel/Topic Segmentation
- Use topics/rooms for multi-tenant isolation.

```json
{
  "action": "subscribe",
  "topic": "tenant:abc123:simulation:sim-456"
}
```

### c. Message Envelope
- Include envelope metadata: type, timestamp, correlationId, tenantId.

```json
{
  "type": "simulationUpdate",
  "tenantId": "abc123",
  "data": { "id": "sim-456", "progress": 0.85 },
  "timestamp": "2025-09-05T10:55:00Z"
}
```

### d. Backpressure & Rate Limiting
- Detect slow clients and drop/queue messages.
- Throttle message rates per connection.

---

## 4. Cross-Cutting Patterns

- **Observability:** Trace per-request/connection logs and metrics; propagate correlation IDs.
- **API Gateway:** Centralize auth, rate limiting, and routing.
- **Schema Evolution:** Support additive changes and deprecate fields/methods gracefully.
- **Multi-Tenancy:** Propagate tenant context through all API calls and websockets.
- **Error Handling:** Standardize error formats and codes.

---

## References

- [RESTful API Design Guidelines](https://restfulapi.net/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [WebSocket Patterns](https://ably.com/concepts/websockets)