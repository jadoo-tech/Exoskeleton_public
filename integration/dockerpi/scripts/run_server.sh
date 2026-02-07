#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${DOCKERPI_USER:-pi}"
PASSWORD="${DOCKERPI_PASSWORD:-}"

SSH_OPTS=(
  -p 6022
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
)

if [ -n "$PASSWORD" ] && command -v sshpass >/dev/null 2>&1; then
  SSH_PREFIX=(sshpass -p "$PASSWORD")
else
  SSH_PREFIX=()
fi

"${SSH_PREFIX[@]}" ssh "${SSH_OPTS[@]}" "${USER_NAME}"@localhost <<'EOF'
set -euo pipefail

cd /home/pi/exo
python3 -m pip install --user flask gunicorn numpy opencv-python pillow pyserial werkzeug

python3 - <<'PY'
from pathlib import Path

path = Path('/home/pi/exo/Server/Web Page/backend/constants.py')
text = path.read_text()
text = text.replace("HOST = '10.57.43.134'", "HOST = '0.0.0.0'")
path.write_text(text)
print('Updated server HOST to 0.0.0.0')
PY

pkill -f "gunicorn.*app:app" || true

cd "/home/pi/exo/Server/Web Page/backend"
nohup python3 -m gunicorn -w 1 -b 0.0.0.0:8000 app:app > /home/pi/server.log 2>&1 &

echo "Server started. Log: /home/pi/server.log"
EOF

echo "Host endpoint: http://localhost:18000"
