#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$ROOT_DIR/backups/$TIMESTAMP"
INSTANCE_DIR="$ROOT_DIR/instance"
DB_FILE="$INSTANCE_DIR/labdesk.sqlite"
UPLOADS_DIR="$INSTANCE_DIR/uploads"

cd "$ROOT_DIR"

if [[ ! -f "$DB_FILE" ]]; then
  echo "Database file not found at $DB_FILE"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
cp "$DB_FILE" "$BACKUP_DIR/labdesk.sqlite"

if [[ -d "$UPLOADS_DIR" ]]; then
  cp -R "$UPLOADS_DIR" "$BACKUP_DIR/uploads"
fi

echo "Backup created at $BACKUP_DIR"
