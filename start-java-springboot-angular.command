#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$ROOT_DIR/java-springboot-angular"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="$HOME/Library/Logs/ProfessionalVideoDownloaderPro"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
NPM_CACHE_DIR="$HOME/Library/Caches/ProfessionalVideoDownloaderPro/npm"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

JAVA21_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
if [[ -d "$JAVA21_HOME" ]]; then
  export JAVA_HOME="$JAVA21_HOME"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

export npm_config_cache="$NPM_CACHE_DIR"

cleanup() {
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

for cmd in mvn node npm; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd was not found in PATH."
    exit 1
  fi
done

if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
  echo "Project folders were not found."
  exit 1
fi

mkdir -p "$LOG_DIR"
mkdir -p "$NPM_CACHE_DIR"
: > "$BACKEND_LOG"
: > "$FRONTEND_LOG"

echo "Starting backend..."
(cd "$BACKEND_DIR" && mvn spring-boot:run) >> "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

sleep 5

cd "$FRONTEND_DIR"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting frontend..."
npm start >> "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo
echo "Backend log: $BACKEND_LOG"
echo "Frontend log: $FRONTEND_LOG"
echo "Open http://localhost:4200 after the frontend finishes starting."
echo "Press Ctrl+C to stop both services."
echo

tail -n +1 -f "$BACKEND_LOG" "$FRONTEND_LOG"
