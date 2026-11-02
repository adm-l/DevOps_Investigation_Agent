# Installation and run

## Requirements
- Python 3.12+
- Ollama running locally
- A tool-calling-capable Ollama model (start with qwen3:4b)

## Clone and configure
```bash
git clone https://github.com/adm-l/DevOps_Investigation_Agent.git
cd DevOps_Investigation_Agent
cp .env.example .env
```
Edit `.env`; use a unique API key of at least 16 characters.

## Start Ollama
```bash
ollama pull qwen3:4b
ollama serve
curl http://localhost:11434/api/tags
``
If Ollama already runs as a background service, do not start a second instance.

## Install Python dependencies
macOS/Linux:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
``
Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
``

## Run API
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
``
The app starts four MCP stdio subprocesses. Do not launch them separately during normal API operation. Swagger: http://127.0.0.1:8000/docs

## Test
```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl -X POST http://localhost:8000/api/v1/investigations \
 -H "Content-Type: application/json" -H "X-API-Key: change-this-local-key" \
 -d '{"service":"payment-service","incident":"Elevated HTTP 5xx and database timeout errors"}'
pytest -q
```
Replace the sample API key with the value in your `.env`.

## Docker Compose
Ollama is expected to run on the host; Compose runs the API and its MCP subprocesses in one container.
```bash
cp .env.example .env
docker compose up --build
``
Compose uses `host.docker.internal:11434`. Adjust this for Linux hosts where that name is unavailable. Stop with `docker compose down`.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| API_KEY | API authentication | local example key |
| OLLAMA_BASE_URL | Ollama endpoint | localhost:11434 |
| OLLAMA_MODEL | Model | qwen3:4b |
| OLLAMA_TIMEOUT_SECONDS | Model timeout | 90 |
| MCP_TOOL_TIMEOUT_SECONDS | Tool timeout | 20 |
| AGENT_MAX_STEPS | Agent turns | 8 |
| AGENT_MAX_PARALLEL_TOOLS | Concurrent calls | 4 |
| RATE_LIMIT_REQUESTS | Requests per window | 30 |
| RATE_LIMIT_WINDOW_SECONDS | Window | 60 |

## Troubleshooting
- Connection refused: verify Ollama is running and reachable from the API/container.
- Model not found: run `ollama pull qwen3:4b` or change OLLAMA_MODEL.
- No tool calls: verify the selected model supports tool calling.
- Import errors: activate .venv and reinstall dependencies.
- MCP startup failure: verify Python version and installed mcp SDK. The manager launches servers using the same Python interpreter as the API.
