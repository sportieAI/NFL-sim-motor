# API Reference

## Authentication

- All API endpoints require an API key or OAuth2 token.
- Example header:
  ```
  Authorization: Bearer YOUR_API_KEY
  ```

## Endpoints

### `POST /simulate`

- Run a new simulation.
- **Body:**  
  ```json
  {
    "teams": ["KC", "SF"],
    "mode": "playoff",
    "agents": ["default"]
  }
  ```
- **Response:** Simulation ID, status, and results link.

### `GET /simulation/{id}`

- Retrieve results for a specific simulation.

### `POST /narrate`

- Generate voice or text commentary for a simulation.
- **Body:**  
  ```json
  {
    "simulation_id": "abc123",
    "voice": "coqui"
  }
  ```

## Usage Patterns

- Simulations are asynchronous; poll or subscribe for completion.
- Webhooks available for notification.

## Errors

- Standard HTTP status codes.
- Error details in JSON under `error` key.
