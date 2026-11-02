.PHONY: install run test lint compose-up compose-down
install:
	python -m pip install -e ".[dev]"
run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
test:
	pytest -q
lint:
	ruff check app tests
compose-up:
	docker compose up --build -d
compose-down:
	docker compose down
