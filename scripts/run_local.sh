#!/usr/bin/env bash
set -euo pipefail
if [[ ! -d .venv ]]; then python3.12 -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
if [[ ! -f .env ]]; then cp .env.example .env; echo "Review .env and set a private API_KEY."; fi
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
