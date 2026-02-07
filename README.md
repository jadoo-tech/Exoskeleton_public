# Exoskeleton Repo

This repository contains the software and hardware artifacts for the Jadoo exoskeleton project.

- Server web/backend code: `Server/Web Page/`
- Client runtime code (typo kept from original repo): `Cilent/`
- MCU firmware: `Microcontroller Codes/`
- PCB design/fabrication files: `Kicad Files/`

## Current communication stack

The active software path is now the **v2 communication stack** (session-based, multi-client aware):

- Server connection manager: `Server/Web Page/backend/comm/manager.py`
- Server app entrypoint: `Server/Web Page/backend/app.py`
- Client agent: `Cilent/agent.py`
- Client launcher: `Cilent/main.py`

Legacy client scripts (`execCommands.py`, `videoDisplay.py`, `updateData.py`) are still present for fallback and reference.

## Local macOS bring-up (no hardware required)

1. Install/sync environment:

```bash
uv sync --group test
```

2. Start local emulated stack:

```bash
integration/macos/start_local_stack.sh
```

3. Open the UI:

- `http://127.0.0.1:5050`
- `http://127.0.0.1:5050/motionControls`

4. Stop when done:

```bash
integration/macos/stop_local_stack.sh
```

## Runtime env vars (important)

- `EXO_HOST`: server IP used by server/client socket listeners/connectors
- `EXO_CLIENT_ID`: logical client identity for v2 registration
- `EXO_COMM_STACK`: `v2` (default) or `legacy`
- `EXO_SIM_MODE`: `1` to run client without serial/camera hardware
- `EXO_HTTP_HOST`, `EXO_HTTP_PORT`: Flask bind host/port

## Observability endpoints

- `GET /health`
- `GET /clients`
- `GET /commandStatus/<msg_id>`

`POST /commandClient` still drives commands from the Motion Control UI.

## Integration status

- `integration/macos/tests` currently pass.
- `integration/dockerpi/` is work-in-progress and currently not reliable on this machine.
