#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TMP_DIR="$SCRIPT_DIR/../.tmp"
PAYLOAD="$TMP_DIR/exo-runtime.tar.gz"
USER_NAME="${DOCKERPI_USER:-pi}"
PASSWORD="${DOCKERPI_PASSWORD:-}"

SSH_BASE_OPTS=(
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
)

if [ -n "$PASSWORD" ] && command -v sshpass >/dev/null 2>&1; then
  SSH_PREFIX=(sshpass -p "$PASSWORD")
else
  SSH_PREFIX=()
fi

wait_for_ssh_port() {
  local port="$1"
  local deadline=$((SECONDS + 240))
  until nc -z localhost "$port" >/dev/null 2>&1; do
    if [ "$SECONDS" -ge "$deadline" ]; then
      echo "Timed out waiting for SSH on localhost:${port}" >&2
      exit 1
    fi
    sleep 2
  done
}

wait_for_ssh_login() {
  local port="$1"
  local deadline=$((SECONDS + 600))

  until "${SSH_PREFIX[@]}" ssh -p "$port" "${SSH_BASE_OPTS[@]}" -o ConnectTimeout=5 "${USER_NAME}"@localhost "echo ready" >/dev/null 2>&1; do
    if [ "$SECONDS" -ge "$deadline" ]; then
      echo "Timed out waiting for SSH login on localhost:${port}" >&2
      exit 1
    fi
    sleep 3
  done
}

run_scp() {
  local port="$1"
  "${SSH_PREFIX[@]}" scp -P "$port" "${SSH_BASE_OPTS[@]}" "$PAYLOAD" "${USER_NAME}"@localhost:/home/pi/exo-runtime.tar.gz
}

run_ssh() {
  local port="$1"
  local cmd="$2"
  "${SSH_PREFIX[@]}" ssh -p "$port" "${SSH_BASE_OPTS[@]}" "${USER_NAME}"@localhost "$cmd"
}

mkdir -p "$TMP_DIR"

tar -czf "$PAYLOAD" \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  -C "$REPO_ROOT" \
  "Server/Web Page/backend" \
  "Server/Web Page/html" \
  "Server/Web Page/static" \
  "Cilent" \
  "pyproject.toml" \
  "uv.lock" \
  "integration/dockerpi/client_emulator.py"

for port in 6022 7022; do
  wait_for_ssh_port "$port"
  wait_for_ssh_login "$port"
  run_scp "$port"
  run_ssh "$port" "mkdir -p /home/pi/exo && tar -xzf /home/pi/exo-runtime.tar.gz -C /home/pi/exo"
done

echo "Runtime payload copied to both VMs under /home/pi/exo"
