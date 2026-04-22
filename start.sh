#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$HOME/.local/share/azrael-downloader/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

install_pkg() {
  local pkg="$1"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y "$pkg"
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y "$pkg"
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --noconfirm "$pkg"
  elif command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y "$pkg"
  else
    echo "Cannot install $pkg: no supported package manager found."
    exit 1
  fi
}

ensure_cmd() {
  local cmd="$1"
  local pkg="${2:-$1}"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Installing $pkg..."
    install_pkg "$pkg"
  fi
}

ensure_cmd java openjdk-21-jdk
ensure_cmd mvn maven
ensure_cmd node nodejs
ensure_cmd npm npm
ensure_cmd yt-dlp yt-dlp
ensure_cmd ffmpeg ffmpeg

cleanup() {
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
  echo "Project folders not found."
  exit 1
fi

mkdir -p "$LOG_DIR"
: > "$BACKEND_LOG"
: > "$FRONTEND_LOG"

echo "Starting backend..."
(cd "$BACKEND_DIR" && mvn -q spring-boot:run) >> "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo "Waiting for backend to be ready..."
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8080/api/system/dependencies >/dev/null 2>&1; then
    echo "Backend ready."
    break
  fi
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend crashed. Check $BACKEND_LOG"
    exit 1
  fi
  sleep 2
done

cd "$FRONTEND_DIR"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm ci
fi

echo "Starting frontend..."
npm start >> "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo "Waiting for frontend to be ready..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:4200 >/dev/null 2>&1; then
    echo "Frontend ready."
    break
  fi
  sleep 2
done

echo
echo "Backend:  http://127.0.0.1:8080"
echo "Frontend: http://localhost:4200"
echo "Logs:     $LOG_DIR"
echo "Press Ctrl+C to stop both services."
echo

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:4200 &
fi

tail -n +1 -f "$BACKEND_LOG" "$FRONTEND_LOG"
