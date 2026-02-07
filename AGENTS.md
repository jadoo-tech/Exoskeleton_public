# Exoskeleton Repo Map (Recovery Notes)

This file captures the current state of the repository so a new maintainer can quickly understand what is active, what is legacy, and where likely integration problems are.

## 1) High-level project shape

The repo is a mix of:
- Raspberry Pi server/web app code.
- Raspberry Pi client code that talks to hardware over serial.
- Arduino/Teensy sketches for motor/display/sensor subsystems.
- KiCad PCB design files and fabrication exports.
- Papers/reference documents.

Most likely active runtime path today is:
- `Server/Web Page/backend/` (Flask + socket server logic)
- `Server/Web Page/html/` + `Server/Web Page/static/` (UI)
- `Cilent/` (client runtime; folder name is misspelled in repo)

## 2) Top-level directory map

- `README.md`
  - Very short top-level note from prior student.

- `Server/`
  - Main server-side code and an old testing area.

- `Cilent/`
  - Main client-side Raspberry Pi code (typo: should probably be `Client`).

- `Microcontroller Codes/`
  - Arduino/Teensy firmware and one EEG notebook.

- `Kicad Files/`
  - Hardware design projects, libraries, and many generated manufacturing outputs.

- `pdfs/`
  - Research/reference PDFs.

- `Papers:documents/`
  - Appears effectively empty (only `.DS_Store` at time of review).

## 3) Server runtime map

### 3.1 Web/backend code (`Server/Web Page/backend/`)

- `app.py`
  - Flask app serving pages and API routes.
  - Hosts control endpoint: `POST /commandClient`.
  - Hosts data endpoint: `GET /fetchData` (reads `data.csv`).
  - Hosts video endpoint: `GET /video_feed/<client_id>` (MJPEG stream).
  - Opens raw TCP sockets for client command and video channels.

- `constants.py`
  - Network config and protocol constants:
    - `HOST = '10.57.43.134'`
    - `PORTIN = 9158` (client -> server file/data)
    - `PORTOUT = 1863` (server -> client commands)
    - `PORT_VIDEO = 8612` (client -> server video)
    - shared `ENDWORD`/`STARTSEND` markers.
  - Contains note: `TODO: Implement mulitple connection`.

- `recvFile.py`
  - Standalone receiver for uploaded file payloads on `PORTIN`.
  - Not currently wired into `app.py` runtime path.

- `videoDisplay.py`
  - Standalone OpenCV receiver/viewer for incoming video.
  - Useful for debugging camera stream outside Flask pages.

- `data.csv`
  - Placeholder/demo table data served to frontend.

- `README.md`
  - Explicitly says CSV update thread is not implemented in `app.py` yet.

### 3.2 UI code (`Server/Web Page/html/` + `static/`)

- `html/Home.html`
  - Landing page with simple menu/login mock behavior.

- `html/MotionControl.html`
  - Control UI for commands and video stream start.

- `html/DataDisplay.html`
  - Displays rows fetched from `/fetchData`.

- `static/javascript/MotionControl.js`
  - Sends command payloads like:
    - `step <n> on Client: <id>`
    - `display <idx> <text> on Client: <id>`
    - `start_video on Client: <id>`

- `static/javascript/DataDisplay.js`
  - Polls `/fetchData` every 5 seconds and rebuilds table.

- `static/javascript/Home.js`
  - Mock login/dropdown behavior.

- CSS/images in `static/css/`
  - Styling and background assets for the three pages.

### 3.3 Nginx config (`Server/Web Page/nginx/`)

- Includes an `nginx.conf` plus `sites-available/default`.
- `default` proxies `location /` to Flask/Gunicorn at `127.0.0.1:8000`.
- Also contains mostly stock nginx support files.

## 4) Client runtime map (`Cilent/`)

- `main.py`
  - Thread launcher that starts:
    - `updateData.py`
    - `execCommands.py`
    - `videoDisplay.py`

- `constants.py`
  - Mirrors server host/ports and protocol words.
  - Defines serial device paths used by command executor:
    - `MOTOR_SERIALPORT = "/dev/ttyUSB0"`
    - `OLED_SERIALPORT = "/dev/ttyACM0"`

- `execCommands.py`
  - Connects to server command port (`PORTIN` from client perspective).
  - Receives text commands and dispatches:
    - `step` -> send serial command to motor controller.
    - `display` -> send serial command to OLED controller.
    - `start_video` -> currently no direct action (video script already runs separately from `main.py`).

- `updateData.py`
  - Connects to server data port and uploads file content once.

- `videoDisplay.py`
  - Captures camera frames via `picamera2`, JPEG-encodes, sends to server video port.

- `camTest.py`
  - Quick camera test script.

- `Old Test Codes/`
  - Experimental/legacy code; not clean enough to treat as production.

## 5) Microcontroller firmware map (`Microcontroller Codes/`)

- `Limbs_Motor/Limbs_Motor.ino`
  - Stepper motor serial command interpreter.
  - Supports command format: `step <steps>`.

- `AR/AR.ino`
  - Dual OLED display control.
  - Supports serial command: `display <index> <word>`.

- `Limbs/Limbs.ino`
  - IMU data readout (FastIMU/LSM6DSL based).

- `EEG-Teensy` folder (actual repo folder uses a non-standard dash)
  - `EEG/EEG.ino` for EEG-related sampling/control output.

- `I2C_Address_detector/I2C_Address_detector.ino`
  - Generic I2C scanner for board bring-up.

- `Potentiometer_DS3502/Potentiometer_DS3502.ino`
  - DS3502 digital potentiometer test.

- `Motor-Old/`
  - Prior motor test sketch + wiring/spec assets.

- `eeg_classification_program.ipynb`
  - Notebook likely for post-processing/classification experiments.

## 6) KiCad map (`Kicad Files/`)

Large hardware archive. Mostly not runtime software.

Main subprojects include:
- `AR Glass/`
- `EEG kicad/`
- `EEG - Seperated/` (repo spelling)
- `Heater/`
- `KiCad Libraries/`
- `Old/`

Contains many generated outputs (`.zip`, Gerbers, drill files, backups) plus active design sources (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`).

## 7) End-to-end communication model (as implemented)

1. Operator uses browser UI -> Flask endpoint `/commandClient`.
2. Flask sends raw TCP command string to client (`PORTOUT` server side = 1863).
3. Client `execCommands.py` receives command and writes serial commands to connected microcontrollers.
4. Client `videoDisplay.py` streams JPEG frames to server (`PORT_VIDEO` = 8612).
5. Flask exposes latest frame buffers via `/video_feed/<client_id>` for webpage display.
6. Client `updateData.py` can upload a file to server data socket (`PORTIN` = 9158), but backend integration is incomplete.

## 8) Why multi-client likely failed (current code risks)

Primary issues visible in code:

- `CLIENTNUM` is not actually implemented in current Flask path (`constants.py` TODO still present).
- `initialize_Connection(cId)` blocks on two sequential `accept()` calls (command socket and video socket), which can stall command setup.
- No client registration/identity handshake at socket layer; UI-supplied `cId` is trusted and mapped to next accepted socket.
- `listen(1)` backlog is used in active path; not designed for concurrent burst connections.
- `commandClient()` can send `start_video` twice in one request path.
- Data upload receiver (`recvFile.py`) exists but is not threaded into active Flask runtime as noted in backend README.

## 9) Known quality issues found during inspection

- Folder naming/typos: `Cilent`, `mulitple`, `Ngnix`, etc.
- No dependency lock/manifests (`requirements.txt`, `pyproject.toml`, `package.json` absent).
- Multiple hard-coded IP assumptions (`10.57.43.134`) in constants files.
- Old test scripts contain syntax/indentation errors (legacy quality; not production-ready).
- Frontend has minor rough edges (placeholder login logic, hard-coded image paths in `Home.html`).

## 10) Quick bring-up checklist for future maintainers

1. Set `HOST` consistently in:
   - `Server/Web Page/backend/constants.py`
   - `Cilent/constants.py`
2. Ensure firewall rules allow TCP ports `9158`, `1863`, `8612` on server Pi.
3. Start Flask app (typically behind Gunicorn/Nginx, per server README notes).
4. On client Pi, run `python3 main.py` in `Cilent/`.
5. Verify command channel first (`step`, `display`) before video.
6. Treat multi-client support as unfinished and requiring refactor.

## 11) Practical next engineering step

If this project is being revived, safest path is:
- Stabilize single-client mode first (health checks + reconnect logic + explicit protocol framing).
- Then add a real client identity handshake and connection manager for multi-client support.

## 12) Who made what when (git forensics)

Repository history range:
- First commit in this repo: 2024-08-28 (`3ef8fdd`, "working base", author `Yena Kang`).
- Latest commit in this repo: 2025-10-02 (`dcfb2c9`, "Update", author `Yena Kang`).

Contributor identity notes (based on commit emails):
- `Yena Kang` and `ykang1011` share `119773109+ykang1011@users.noreply.github.com` and appear to be the same person using two display names.
- `CorruptedJef`, `jyliu-desktop1-windows`, `jyliu-laptop1`, and `jyliu-laptop1-windows` all use `jliueducation@gmail.com` and appear to be the same contributor across devices.
- `Jeffrey` appears both as `86396381+jyliu24@users.noreply.github.com` and `86396381+CorruptedJef@users.noreply.github.com` (likely same person/alias family as above).

High-confidence ownership by subsystem:
- Runtime software (`Server/Web Page/backend`, `Server/Web Page/html`, `Server/Web Page/static`, `Cilent`) is overwhelmingly Yena/ykang.
  - Initial implementation: 2024-08-28.
  - Video-stream additions/fixes: 2024-09-24 and 2025-06-28.
  - Broad refresh/update: 2025-10-02.
- EEG KiCad work has notable contributions from August Nguyen (2024-10 to 2024-11) in `Kicad Files/EEG kicad`.
- Heating/limb PCB work is heavily associated with Jeffrey/CorruptedJef/jyliu aliases (2024-11 through 2025-03).
- `eeg_classification_program.ipynb` was added by `abhishekamitroy` (2024-11-18).

Notable timeline:
- 2024-08 to 2024-09: initial server/client/web architecture and early video tests.
- 2024-10 to 2025-03: intense KiCad/PCB iteration (EEG, heater, limb boards).
- 2025-06: active client/server video path revisions.
- 2025-09: repo restructuring/revert activity around server and hardware folders.
- 2025-10: latest all-in update touching server/client runtime files.

## 13) Hardware setup inferred from code and hardware artifacts

### 13.1 Core runtime hardware path (the one tied to web controls)

- `Server Pi`
  - Runs Flask/Gunicorn/Nginx web app from `Server/Web Page/`.
- `Client Pi` (folder `Cilent/`)
  - Runs command receiver + data sender + camera streamer.
  - Connects to server via TCP ports 9158 (data), 1863 (commands), 8612 (video).
- `Motor controller MCU` (Arduino-class)
  - Connected to client Pi serial port `/dev/ttyUSB0` (`Cilent/constants.py`).
  - Expects serial command `step <N>` (`Cilent/execCommands.py`, `Microcontroller Codes/Limbs_Motor/Limbs_Motor.ino`).
  - Motor-driver output color notes are in `Microcontroller Codes/Motor-Old/Connection.jpeg`.
- `OLED controller MCU`
  - Connected to client Pi serial port `/dev/ttyACM0` (`Cilent/constants.py`).
  - Expects serial command `display <index> <word>` (`Cilent/execCommands.py`, `Microcontroller Codes/AR/AR.ino`).
- `Camera`
  - Client Pi uses `picamera2` (`Cilent/videoDisplay.py`), so this expects a Raspberry Pi camera attached and enabled.

### 13.2 Additional hardware subsystems in repo

- AR Glasses controller wiring appears documented in:
  - `Kicad Files/AR Glass/AugmentedGlassesPinout_v1.pdf`
  - Includes Raspberry Pi Pico pin mappings for two Waveshare transparent OLED drivers and an HM01B0 Arducam module.
- Limb/heater board hardware is documented in:
  - `Kicad Files/Heater/Limb_Circuit.kicad_sch`
  - `Kicad Files/Heater/Exoskeleton BOM - Limb Circuit.csv`
  - BOM includes Arduino Nano + MAX31855 thermocouple interface + LSM6DSL IMU + XT60 connectors for input/heater/thermocouple.
- EEG design artifacts exist in:
  - `Kicad Files/EEG kicad/`
  - `Kicad Files/EEG - Seperated/`
  - Runtime Teensy sketch in `Microcontroller Codes/EEG-Teensy/EEG/EEG.ino` (folder uses a special dash character in actual name).

### 13.3 Important unknowns

- There is no single, authoritative final wiring document for the full assembled exoskeleton in this repo.
- Multiple PCB generations coexist; "latest fabricated/installed" is not explicitly tagged.
- The runtime software references motor/OLED serial devices and camera, but does not explicitly integrate EEG or heater subsystems end-to-end.

## 14) Practical boot-up runbook (single-client, highest chance of success)

### 14.1 Prepare hardware and firmware

1. Flash MCU firmware:
   - Motor MCU: `Microcontroller Codes/Limbs_Motor/Limbs_Motor.ino`
   - OLED MCU: `Microcontroller Codes/AR/AR.ino`
   - Optional IMU/EEG/heater sketches as needed for your hardware branch.
2. Connect client Pi USB devices and verify serial nodes:
   - `ls /dev/tty*` and confirm expected `/dev/ttyUSB0` and `/dev/ttyACM0`.
3. Attach Pi camera to client Pi and enable camera stack for `picamera2`.

### 14.2 Configure networking

1. Set the same server IP in both:
   - `Server/Web Page/backend/constants.py` -> `HOST`
   - `Cilent/constants.py` -> `HOST`
2. Ensure server firewall allows TCP `9158`, `1863`, `8612`.

### 14.3 Install Python dependencies (manual, because no lockfile)

Server-side expected imports imply at least:
- `flask`, `werkzeug`, `opencv-python`, `numpy`

Client-side expected imports imply at least:
- `pyserial`, `picamera2`, `Pillow`

Also needed operationally:
- `gunicorn` (per server README)

### 14.4 Start server

1. From `Server/Web Page/backend/`, start Flask app via gunicorn (as described in server README), typically on `127.0.0.1:8000`.
2. If using nginx, use `Server/Web Page/nginx/sites-available/default` style config to proxy `/:80` -> `127.0.0.1:8000`.
3. Confirm browser access to `/`, `/motionControls`, `/dataDisplay`.

### 14.5 Start client

1. On client Pi, run `python3 main.py` in `Cilent/`.
2. This launches `updateData.py`, `execCommands.py`, and `videoDisplay.py` threads/subprocesses.

### 14.6 Functional smoke test

1. Open Motion Control page.
2. Enter a client ID (any string in current implementation).
3. Send `step` command and verify motor response.
4. Send `display` command and verify OLED response.
5. Start video and verify `img` stream from `/video_feed/<client_id>`.

### 14.7 Known runtime caveats while booting

- Multi-client operation is unfinished and likely to stall because `accept()` is blocking and there is no proper identity handshake.
- `start_video` request path can result in duplicate command send attempts.
- Data upload (`updateData.py` -> `recvFile.py`) is not integrated into the main Flask runtime thread.

## 15) 2026-02 refactor update (current software status)

The runtime communication path has started a major replacement aligned with `CLIENT_CONN_MIGRATION.md`:

- New server connection manager lives in `Server/Web Page/backend/comm/manager.py`.
- New Flask backend path in `Server/Web Page/backend/app.py` now uses session-based client registration.
- New client agent lives in `Cilent/agent.py` and is launched by `Cilent/main.py` when `EXO_COMM_STACK=v2` (default in `Cilent/constants.py`).
- Legacy scripts (`execCommands.py`, `videoDisplay.py`) are still present for fallback and archaeology.

What changed versus the legacy path:

- Server no longer pairs clients by sequential blocking `accept()` calls tied to UI-provided client IDs.
- Client now explicitly registers over control channel (`hello`/`hello_ack`) and gets a server-issued `session_id`.
- Video channel now requires `video_hello` with matching `client_id` + `session_id` before frames are accepted.
- Server tracks heartbeat and drops stale sessions.
- Command lifecycle now supports acknowledgement and result tracking.

## 16) New server endpoints and observability

In addition to legacy UI routes, backend now exposes:

- `GET /health`
  - Basic service health and comm manager running state.
- `GET /clients`
  - Active client/session list and whether video is connected.
- `GET /commandStatus/<msg_id>`
  - Per-command lifecycle state (`ack`, `result`, timestamps).

`POST /commandClient` remains the primary UI command endpoint and now returns a `msg_id` for tracking.

## 17) Practical bring-up (v2 comm stack)

Server:

1. Set env vars as needed (`EXO_HOST`, `EXO_HTTP_HOST`, `EXO_HTTP_PORT`).
2. Run from `Server/Web Page/backend/`:
   - `uv run python app.py`

Client:

1. Set env vars (`EXO_HOST`, `EXO_CLIENT_ID`, optional `EXO_SIM_MODE=1`).
2. Run from `Cilent/`:
   - `uv run python main.py`

For local macOS emulation without hardware:

- Start stack: `integration/macos/start_local_stack.sh`
- Stop stack: `integration/macos/stop_local_stack.sh`
- UI: `http://127.0.0.1:5050/motionControls`

## 18) Current test status (as of this update)

- `integration/macos/tests` pass against the new v2 protocol path.
- Playwright smoke test against `motionControls` passes for:
  - `start_video`
  - `step`
  - `display`
  - MJPEG render from `/video_feed/<client_id>`
- `integration/dockerpi/` remains work-in-progress:
  - Not reliable yet on this machine due VM boot/SSH readiness instability.
