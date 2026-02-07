#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/../docker-compose.yml"

mkdir -p "$SCRIPT_DIR/../state/server" "$SCRIPT_DIR/../state/client"
docker-compose -f "$COMPOSE_FILE" up -d --build

cat <<'MSG'

dockerpi pair is starting.
VM boot takes a few minutes.

Next steps:
  1) integration/dockerpi/scripts/push_runtime.sh
  2) integration/dockerpi/scripts/run_server.sh
  3) integration/dockerpi/scripts/run_client_emulator.sh

MSG
