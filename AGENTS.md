# Exoskeleton Current State

This file is a compact snapshot of what is active in the repo right now.

## Runtime architecture (active)

- Communication stack is **v2** (session-based), not the old sequential socket-pairing flow.
- Server side:
  - `Server/Web Page/backend/app.py`
  - `Server/Web Page/backend/comm/manager.py`
- Client side:
  - `Cilent/main.py` launches scripts from `Cilent/constants.py`
  - default script is `Cilent/agent.py` when `EXO_COMM_STACK=v2`

## What v2 does

- Client registers on control channel with `hello`; server replies `hello_ack` + `session_id`.
- Client sends heartbeat; server drops stale sessions by timeout.
- Commands are sent with IDs and tracked with:
  - `command_ack`
  - `command_result`
- Video channel requires `video_hello` with matching `client_id` + `session_id`.

## Current web pages

- `/motionControls` - legacy-style multi-client control table.
- `/exoDashboard` - connected client list.
- `/exoDashboard/client/<client_id>` - single-client page with:
  - live video
  - controls (`start_video`, `step`, `display`)
  - command history table
- `/dataDisplay` - currently displays placeholder CSV data.

## Current API endpoints

- `POST /commandClient` - send command in format `<command> on Client: <id>`.
- `GET /video_feed/<client_id>` - MJPEG stream for client.
- `GET /clients` - active sessions and video-connected state.
- `GET /commandStatus/<msg_id>` - ack/result for one command.
- `GET /commandHistory/<client_id>?limit=<n>` - recent commands for client.
- `GET /health` - backend health + comm manager running state.
- `GET /fetchData` - rows from `Server/Web Page/backend/data.csv`.

## Local macOS workflow (current)

Use these scripts:

- `integration/macos/start_local_stack.sh`
- `integration/macos/stop_local_stack.sh`

`start_local_stack.sh` currently launches:

- server on `http://127.0.0.1:5050`
- two simulated clients: `local1`, `local2`

Log files:

- `integration/macos/logs/server.log`
- `integration/macos/logs/client-local1.log`
- `integration/macos/logs/client-local2.log`

## Important env vars

- `EXO_HOST` - server host used by socket layers.
- `EXO_HTTP_HOST`, `EXO_HTTP_PORT` - Flask bind target.
- `EXO_COMM_STACK` - `v2` (default) or `legacy`.
- `EXO_CLIENT_ID` - client identity for v2 registration.
- `EXO_SIM_MODE=1` - no serial/camera hardware required.

## Known status and gaps

- `integration/macos/tests` currently pass for the active stack.
- `integration/dockerpi/` is still work-in-progress (not stable yet here).
- `dataDisplay` is not live telemetry yet; it serves static/demo CSV rows.
- Legacy client scripts remain in repo for fallback/archeology:
  - `execCommands.py`
  - `videoDisplay.py`
  - `updateData.py`
