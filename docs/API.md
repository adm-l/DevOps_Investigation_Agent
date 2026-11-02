# API

## GET /health/live
Liveness endpoint; no authentication.

## GET /health/ready
Returns MCP server names and tool count after startup; returns 503 before readiness.

## POST /api/v1/investigations
Requires `X-API-Key`.

Request:
```json
{"service":"payment-service","incident":"Elevated HTTP 5xx and database timeout errors"}
```

Response:
```json
{"request_id":"uuid","service":"payment-service","answer":"Evidence-based investigation summary","steps":4,"tools_called":["logs__search_logs","database__get_db_metrics"]}
```

Errors: 401 invalid key; 422 validation; 429 rate limit; 502 Ollama/agent failure; 503 dependencies not ready. Every response includes X-Request-ID.
