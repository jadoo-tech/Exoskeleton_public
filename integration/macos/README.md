# macOS Integration Tests

These tests emulate client sockets and validate the current backend behavior locally.

## Run

```bash
uv sync --group test
uv run pytest integration/macos/tests -q
```

## Run full local stack on macOS

This starts the backend and the client in simulation mode (`EXO_SIM_MODE=1`) so no serial device or Pi camera is required.

```bash
integration/macos/start_local_stack.sh
```

Open:

- `http://127.0.0.1:5050`
- `http://127.0.0.1:5050/motionControls`

Use client id `local1`, click **Start Video**, then send step/display commands.

Stop the stack:

```bash
integration/macos/stop_local_stack.sh
```

## What is covered

- Flask page/data routes return success.
- `/commandClient` can accept a client connection and dispatch command text.
- Video frame ingestion updates `latest_frames`.
- `/video_feed/<client_id>` returns a stream response when frame data exists.

## What is not covered

- Real serial hardware (`/dev/ttyUSB0`, `/dev/ttyACM0`).
- `picamera2` on Raspberry Pi.
- Nginx/Gunicorn deployment behavior.
