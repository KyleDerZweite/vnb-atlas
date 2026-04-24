.PHONY: install dev dev-backend dev-frontend test test-backend typecheck

PYTHON := python
BACKEND_VENV := backend/.venv
BACKEND_PYTHON := $(BACKEND_VENV)/bin/python
BACKEND_PIP := $(BACKEND_VENV)/bin/pip

install:
	$(PYTHON) -m venv $(BACKEND_VENV)
	$(BACKEND_PIP) install --upgrade pip
	cd backend && . .venv/bin/activate && python -m pip install -e ".[dev]"
	cd frontend && npm install

dev:
	./scripts/dev.sh

dev-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

test: test-backend typecheck

test-backend:
	cd backend && . .venv/bin/activate && pytest

typecheck:
	cd frontend && npm run typecheck
