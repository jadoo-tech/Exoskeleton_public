#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${DOCKERPI_USER:-pi}"
PASSWORD="${DOCKERPI_PASSWORD:-}"

if [ -n "$PASSWORD" ] && command -v sshpass >/dev/null 2>&1; then
  exec sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 7022 "${USER_NAME}"@localhost
fi

exec ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 7022 "${USER_NAME}"@localhost
