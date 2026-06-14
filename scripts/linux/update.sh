#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
REMOTE="${REMOTE:-origin}"
TARGET_REF="${1:-}"
SKIP_BACKUP="${SKIP_BACKUP:-0}"

cd "$ROOT_DIR"

if ! command -v git >/dev/null 2>&1; then
  echo "Git was not found."
  exit 1
fi

if [[ ! -d ".git" ]]; then
  echo "This folder is not a Git repository."
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Tracked local changes were found. Commit or discard them before updating."
  exit 1
fi

if [[ "$SKIP_BACKUP" != "1" ]]; then
  "$SCRIPT_DIR/backup.sh"
fi

echo "Fetching updates from $REMOTE..."
git fetch --prune --tags "$REMOTE"

if [[ -z "$TARGET_REF" ]]; then
  REMOTE_HEAD="$(git symbolic-ref --quiet --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null || true)"
  if [[ -n "$REMOTE_HEAD" ]]; then
    TARGET_REF="${REMOTE_HEAD#"$REMOTE/"}"
  else
    TARGET_REF="main"
  fi
fi

RESOLVED_REF=""
DISPLAY_REF="$TARGET_REF"
TARGET_KIND=""

if git show-ref --verify --quiet "refs/tags/$TARGET_REF"; then
  RESOLVED_REF="refs/tags/$TARGET_REF"
  TARGET_KIND="tag"
elif git show-ref --verify --quiet "refs/remotes/$REMOTE/$TARGET_REF"; then
  RESOLVED_REF="refs/remotes/$REMOTE/$TARGET_REF"
  DISPLAY_REF="$REMOTE/$TARGET_REF"
  TARGET_KIND="branch"
elif git rev-parse --verify --quiet "$TARGET_REF^{commit}" >/dev/null; then
  RESOLVED_REF="$TARGET_REF"
  TARGET_KIND="commit"
else
  echo "Could not resolve target ref: $TARGET_REF"
  echo "Use a Git tag such as v0.2.0 or a branch name such as main."
  exit 1
fi

if [[ "$TARGET_KIND" == "branch" ]]; then
  if git show-ref --verify --quiet "refs/heads/$TARGET_REF"; then
    echo "Switching to local branch $TARGET_REF..."
    git switch "$TARGET_REF"
  else
    echo "Creating tracking branch $TARGET_REF from $REMOTE/$TARGET_REF..."
    git switch --track -c "$TARGET_REF" "$REMOTE/$TARGET_REF"
  fi

  git branch --set-upstream-to="$REMOTE/$TARGET_REF" "$TARGET_REF" >/dev/null 2>&1 || true
  echo "Fast-forwarding $TARGET_REF from $REMOTE/$TARGET_REF..."
  git pull --ff-only
elif [[ "$TARGET_KIND" == "tag" || "$TARGET_KIND" == "commit" ]]; then
  echo "Checking out $DISPLAY_REF..."
  git checkout --detach "$RESOLVED_REF"
else
  echo "Unexpected target type for $TARGET_REF"
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python 3 was not found."
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Virtual environment not found. Creating it now..."
  "$PYTHON_BIN" -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mkdir -p instance/uploads
mkdir -p backups

CURRENT_COMMIT="$(git rev-parse --short HEAD)"
echo "Update complete."
if [[ "$TARGET_KIND" == "branch" ]]; then
  echo "Current ref: $TARGET_REF"
else
  echo "Current ref: $DISPLAY_REF"
fi
echo "Current commit: $CURRENT_COMMIT"
echo "Next steps:"
echo "1. Start the app with ./scripts/linux/run.sh"
echo "2. Verify it with ./scripts/linux/healthcheck.sh"
