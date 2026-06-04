#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5000}"
DB_FILE="$ROOT_DIR/instance/labdesk.sqlite"
UPLOADS_DIR="$ROOT_DIR/instance/uploads"
BACKUPS_DIR="$ROOT_DIR/backups"

cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "FAIL: virtual environment not found. Run scripts/linux/setup.sh first."
  exit 1
fi

if [[ ! -f "$DB_FILE" ]]; then
  echo "FAIL: database file not found at $DB_FILE"
  exit 1
fi

if [[ ! -d "$UPLOADS_DIR" ]]; then
  echo "FAIL: uploads directory not found at $UPLOADS_DIR"
  exit 1
fi

if [[ ! -d "$BACKUPS_DIR" ]]; then
  mkdir -p "$BACKUPS_DIR"
fi

.venv/bin/python - <<PY
import sys
import urllib.request

url = "http://${HOST}:${PORT}/"
try:
    with urllib.request.urlopen(url, timeout=5) as response:
        status = response.status
except Exception as exc:  # pragma: no cover
    print(f"FAIL: could not reach {url}: {exc}")
    sys.exit(1)

if status >= 400:
    print(f"FAIL: {url} returned status {status}")
    sys.exit(1)

print(f"OK: app reachable at {url} (status {status})")
PY

echo "OK: database file exists"
echo "OK: uploads directory exists"
echo "OK: backups directory exists"
