#!/usr/bin/env bash
set -euo pipefail

SERVER_IP="${1:-172.30.0.10}"
USER_NAME="${DOCKERPI_USER:-pi}"
PASSWORD="${DOCKERPI_PASSWORD:-}"

SSH_OPTS=(
  -p 7022
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
)

if [ -n "$PASSWORD" ] && command -v sshpass >/dev/null 2>&1; then
  SSH_PREFIX=(sshpass -p "$PASSWORD")
else
  SSH_PREFIX=()
fi

"${SSH_PREFIX[@]}" ssh "${SSH_OPTS[@]}" "${USER_NAME}"@localhost <<EOF
set -euo pipefail

cd /home/pi/exo
python3 -m pip install --user pillow

pkill -f "client_emulator.py" || true

nohup python3 /home/pi/exo/integration/dockerpi/client_emulator.py --host ${SERVER_IP} --fps 6 > /home/pi/client-emulator.log 2>&1 &

echo "Client emulator started. Log: /home/pi/client-emulator.log"
EOF

echo "Client emulator configured to target server at ${SERVER_IP}"
