# DevOps Investigation Agent

A production-oriented multi-MCP reference project. FastAPI starts four independent MCP servers, discovers their tools, namespaces them, and routes Ollama tool calls to the owning MCP session. All infrastructure tools return mock data only.

## MCP servers

| Server | Tools |
|---|---|
| Logs | `search_logs`, `get_error_details` |
| Database | `get_db_metrics`, `get_slow_queries` |
| Kubernetes | `get_pod_status`, `get_deployment_status` |
| GitHub | `get_recent_commits`, `get_open_incidents` |

Public tool names are namespaced, e.g. `logs__search_logs`, to avoid collisions.

## Quick start

Requirements: Python 3.12+, Ollama, and a model with tool-calling support.

```bash
ollama pull qwen3:4b
cp .env.example .env
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
curl http://localhost:8000/health/ready
curl -X POST http://localhost:8000/api/v1/investigations \
  -H "Content-Type: application/json" -H "X-API-Key: change-this-local-key" \
  -d '{"service":"payment-service","incident":"Elevated HTTP 5xx and database timeout errors"}'
```

Use the API key from your own `.env`. Full instructions: [Installation](docs/INSTALLATION.md), [Architecture](docs/ARCHITECTURE.md), [API](docs/API.md), [Operations](docs/OPERATIONS.md).

## Safeguards and scope

- Mock data only; no real systems are accessed or changed.
- API key auth, input validation, request IDs, bounded tool calls and agent steps.
- No shell execution, arbitrary SQL, pod restart, or GitHub write tools.
- The in-memory rate limiter is single-process only; use Redis or a gateway for multiple workers.
- This is a production-minded educational baseline, not a certified production incident platform.

## No GitHub workflows

No GitHub Actions or other workflow files are included. Run tests locally with `pytest -q`.
