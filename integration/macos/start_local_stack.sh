#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_DIR="$SCRIPT_DIR/pids"
WEB_PORT="5050"

mkdir -p "$LOG_DIR" "$PID_DIR"

if [ -f "$PID_DIR/server.pid" ] && kill -0 "$(cat "$PID_DIR/server.pid")" >/dev/null 2>&1; then
  echo "Server already running (pid $(cat "$PID_DIR/server.pid"))"
else
  (
    cd "$REPO_ROOT/Server/Web Page/backend"
    nohup env EXO_HOST=127.0.0.1 EXO_HTTP_HOST=127.0.0.1 EXO_HTTP_PORT=${WEB_PORT} uv run python app.py > "$LOG_DIR/server.log" 2>&1 &
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

if [ -f "$PID_DIR/client.pid" ] && kill -0 "$(cat "$PID_DIR/client.pid")" >/dev/null 2>&1; then
  echo "Client already running (pid $(cat "$PID_DIR/client.pid"))"
else
  (
    cd "$REPO_ROOT/Cilent"
    nohup env EXO_HOST=127.0.0.1 EXO_SIM_MODE=1 EXO_COMM_STACK=v2 EXO_CLIENT_ID=local1 uv run python main.py > "$LOG_DIR/client.log" 2>&1 &
    echo $! > "$PID_DIR/client.pid"
  )
  echo "Started client in SIM_MODE (pid $(cat "$PID_DIR/client.pid"))"
fi

echo
echo "Stack is up:"
echo "  - Web UI: http://127.0.0.1:${WEB_PORT}"
echo "  - Motion Controls: http://127.0.0.1:${WEB_PORT}/motionControls"
echo
echo "In Motion Controls:"
echo "  1) Set client id to local1"
echo "  2) Click Start Video"
echo "  3) Send step/display commands"
echo
echo "Logs:"
echo "  - $LOG_DIR/server.log"
echo "  - $LOG_DIR/client.log"
