#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV="$BACKEND_DIR/.venv"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

require_command python
require_command npm

if [[ ! -d "$BACKEND_VENV" ]]; then
  echo "Creating backend virtual environment..."
  python -m venv "$BACKEND_VENV"
fi

echo "Installing backend dependencies..."
(
  cd "$BACKEND_DIR"
  # shellcheck disable=SC1091
  source "$BACKEND_VENV/bin/activate"
  python -m pip install --upgrade pip
  python -m pip install -e ".[dev]"
)

echo "Installing frontend dependencies..."
(
  cd "$FRONTEND_DIR"
  npm install
)

echo
echo "Starting NRW VNB Atlas in dev mode..."
echo "Backend:  http://127.0.0.1:8000"
echo "OpenAPI:  http://127.0.0.1:8000/docs"
echo "Frontend: http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both processes."
echo

(
  cd "$BACKEND_DIR"
  # shellcheck disable=SC1091
  source "$BACKEND_VENV/bin/activate"
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  npm run dev
) &
FRONTEND_PID=$!

wait -n "$BACKEND_PID" "$FRONTEND_PID"
