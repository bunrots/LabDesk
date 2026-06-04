#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5000}"

cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Virtual environment not found. Run scripts/linux/setup.sh first."
  exit 1
fi

mkdir -p instance/uploads
mkdir -p backups

exec .venv/bin/python -m waitress --host="$HOST" --port="$PORT" app:app
