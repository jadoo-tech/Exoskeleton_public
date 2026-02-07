#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$SCRIPT_DIR/pids"
CLIENT_IDS=("local1" "local2")

stop_pid_file() {
  local name="$1"
  local file="$2"

  if [ ! -f "$file" ]; then
    echo "$name pid file not found"
    return
  fi

  local pid
  pid="$(cat "$file")"

  if kill -0 "$pid" >/dev/null 2>&1; then
    kill "$pid" >/dev/null 2>&1 || true
    for _ in $(seq 1 20); do
      if ! kill -0 "$pid" >/dev/null 2>&1; then
        break
      fi
      sleep 0.2
    done

    if kill -0 "$pid" >/dev/null 2>&1; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    echo "Stopped $name (pid $pid)"
  else
    echo "$name already stopped (stale pid $pid)"
  fi

  rm -f "$file"
}

for client_id in "${CLIENT_IDS[@]}"; do
  stop_pid_file "client ${client_id}" "$PID_DIR/client-${client_id}.pid"
done

# Backward compatibility with old single-client pid file name
stop_pid_file "client" "$PID_DIR/client.pid"
stop_pid_file "server" "$PID_DIR/server.pid"
