# Operations and production hardening

## Implemented
API key authentication, input validation, namespaced tool allowlist, mock read-only tools, bounded agent steps, MCP timeouts, concurrency semaphore, request correlation IDs, non-root container, liveness/readiness endpoints.

## Known limitations
- Rate limiting is in-memory and per process; it resets on restart and is not shared across replicas.
- MCP subprocess failure currently requires application restart; no automated per-server reconnect loop.
- No persistent audit store, distributed tracing, or metrics exporter.
- API key auth is intentionally simple; use an identity provider, secret rotation, and TLS in production.
- Mock data does not prove real integration permissions or correctness.
- Tool output is sent to the model; review data classification and redact secrets.

## Before connecting real infrastructure
Use separate least-privilege credentials per server; define tool-level authorization; keep read and write tools separate; require human approval for destructive actions; validate arguments server-side; redact secrets; store durable audit events; add bounded retries for idempotent operations; implement per-server health/reconnect; use Redis or gateway rate limiting; add OpenTelemetry; pin and scan dependencies/images; apply container resource limits and network policies.

## Mock incident interpretation
Payment mock data correlates application DB-acquisition timeouts, a saturated 50/50 connection pool with 37 waiters, a not-ready pod with restarts, and recent pool/concurrency-related commits. This supports investigating connection-pool pressure, but does not prove root cause. The agent should distinguish evidence from hypotheses.
