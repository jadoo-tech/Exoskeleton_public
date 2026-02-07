#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_DIR="$SCRIPT_DIR/pids"
WEB_PORT="5050"
CLIENT_IDS=("local1" "local2")

mkdir -p "$LOG_DIR" "$PID_DIR"

if [ -f "$PID_DIR/server.pid" ] && kill -0 "$(cat "$PID_DIR/server.pid")" >/dev/null 2>&1; then
  echo "Server already running (pid $(cat "$PID_DIR/server.pid"))"
else
  (
    cd "$REPO_ROOT/Server/Web Page/backend"
    nohup env PYTHONUNBUFFERED=1 EXO_HOST=127.0.0.1 EXO_HTTP_HOST=127.0.0.1 EXO_HTTP_PORT=${WEB_PORT} uv run python -u app.py > "$LOG_DIR/server.log" 2>&1 &
    echo $! > "$PID_DIR/server.pid"
  )
  echo "Started server (pid $(cat "$PID_DIR/server.pid"))"
fi

for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${WEB_PORT}/" >/dev/null; then
    break
  fi
  sleep 0.5
done

if ! curl -sf "http://127.0.0.1:${WEB_PORT}/" >/dev/null; then
  echo "Server did not become ready. Check $LOG_DIR/server.log"
  exit 1
fi

start_client() {
  local client_id="$1"
  local pid_file="$PID_DIR/client-${client_id}.pid"
  local log_file="$LOG_DIR/client-${client_id}.log"

  if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1; then
    echo "Client ${client_id} already running (pid $(cat "$pid_file"))"
    return
  fi

  (
    cd "$REPO_ROOT/Cilent"
    nohup env PYTHONUNBUFFERED=1 EXO_HOST=127.0.0.1 EXO_SIM_MODE=1 EXO_COMM_STACK=v2 EXO_CLIENT_ID="${client_id}" uv run python -u main.py > "$log_file" 2>&1 &
    echo $! > "$pid_file"
  )
  echo "Started client ${client_id} in SIM_MODE (pid $(cat "$pid_file"))"
}

for client_id in "${CLIENT_IDS[@]}"; do
  start_client "$client_id"
done

echo
echo "Stack is up:"
echo "  - Web UI: http://127.0.0.1:${WEB_PORT}"
echo "  - Motion Controls: http://127.0.0.1:${WEB_PORT}/motionControls"
echo "  - Exo Dashboard: http://127.0.0.1:${WEB_PORT}/exoDashboard"
echo
echo "In Motion Controls:"
echo "  1) Set client id to local1 or local2"
echo "  2) Click Start Video"
echo "  3) Send step/display commands"
echo "Or use Exo Dashboard and click a client card"
echo
echo "Logs:"
echo "  - $LOG_DIR/server.log"
for client_id in "${CLIENT_IDS[@]}"; do
  echo "  - $LOG_DIR/client-${client_id}.log"
done
