# CLIENT_CONN_MIGRATION.md

## Objective

Replace the current server-client communication layer with a robust, multi-client-safe architecture while preserving existing exoskeleton control behavior (`step`, `display`, video stream) and web UI workflows.

This plan also includes a **baseline test of current code first** so we can decide whether migration starts from a working snapshot or from known-broken behavior.

---

## Why Replace Current Connection Setup

Current active implementation (`Server/Web Page/backend/app.py` + `Cilent/*.py`) has structural multi-client problems:

- Client identity is supplied by UI text and trusted directly (no transport-level registration/identity binding).
- Command and video sockets are paired by sequential `accept()` timing, not by authenticated client/session identity.
- Blocking `accept()` on command/video channels can stall request flow.
- Backlog is `listen(1)`, fragile under multiple clients.
- Limited reconnect/health handling; no durable command acknowledgements.
- Data upload path is disconnected from main backend flow.

Result: single-client may work; multi-client is nondeterministic and prone to cross-wiring and stalls.

---

## Scope

### In Scope
- Replace server-client control channel.
- Replace video ingest channel.
- Add explicit registration, session management, heartbeat/reconnect.
- Preserve browser API surface where practical (`/commandClient`, `/video_feed/<client_id>`).
- Add observability and diagnostics.
- Add test harness and migration validation gates.

### Out of Scope (initial migration)
- Major UI redesign.
- MCU firmware redesign (`Microcontroller Codes/*` command grammar remains compatible).
- Full DB redesign for all telemetry/history (minimal persistence only if needed).

---

## Guiding Principles

1. **Identity-first**: every channel maps to a verified `client_id` + `session_id`.
2. **Non-blocking I/O**: no request-thread blocking on socket accepts.
3. **Observable by default**: every command has traceable lifecycle.
4. **Backward-compatible where possible**: keep current command semantics.
5. **Incremental rollout**: dual-stack and feature flags to reduce operational risk.

---

## Target Architecture (Recommended)

## Transport Model

- **Control channel**: persistent async connection (WebSocket JSON envelopes).
- **Video channel**: persistent async binary stream (WebSocket binary frames or TCP framed stream with authenticated header).
- **UI/API layer**: Flask routes remain, routed internally to `ConnectionManager`.
- **Client agent**: one process with async tasks (control, video, serial dispatcher, telemetry, reconnect manager).

## Core Server Components

- `ConnectionManager`
  - Tracks clients, sessions, heartbeats, channel state.
- `CommandRouter`
  - Sends command envelopes, tracks `ack` and `result`.
- `VideoFrameStore`
  - Keeps latest frame per client for `/video_feed/<client_id>`.
- `EventLog` (minimal)
  - Structured logs for registration, command send/ack/result, disconnects.

## Core Client Components

- `agent.py` (single orchestrator process)
- `control_transport.py` (register/heartbeat/command receive/ack/result)
- `video_transport.py` (frame capture + push with session binding)
- `command_executor.py` (serial adapters for motor/OLED)
- `telemetry.py` (optional status/events)

---

## Protocol Specification (v1)

All control messages are JSON envelopes:

- `version` (int)
- `type` (string)
- `client_id` (string)
- `session_id` (string)
- `msg_id` (string UUID-ish)
- `ts` (ISO8601)
- `payload` (object)

### Message Types

- `hello`
- `hello_ack`
- `heartbeat`
- `command`
- `command_ack`
- `command_result`
- `error`
- `telemetry` (optional)

### Command Lifecycle

1. Server sends `command`.
2. Client responds quickly with `command_ack` (accepted/rejected).
3. Client executes and sends `command_result` (success/failure + details).
4. Server exposes status to UI/API.

### Identity Rules

- `client_id` is configured on client, not user-entered per command.
- `session_id` issued by server on successful registration.
- Video channel must prove same `client_id` + `session_id`.
- Duplicate active `client_id` policy: reject or replace old session (configurable; default replace stale).

---

## Migration Plan (Phased)

## Phase 0 - Baseline Current System (Do this first)

Goal: determine whether current code can be tested reliably enough to compare pre/post migration behavior.

Tasks:
- Verify current single-client path:
  - Flask route `/commandClient`
  - command dispatch to `Cilent/execCommands.py`
  - video path from `Cilent/videoDisplay.py` to `/video_feed/<client_id>`
- Capture failure signatures:
  - startup order sensitivity
  - timeout/disconnect behavior
  - multi-client misrouting symptoms
- Record baseline metrics:
  - command latency (send -> motor/OLED serial write)
  - frame availability latency
  - reconnect behavior after network drop

Exit criteria:
- We can run repeatable smoke test steps and document observed behavior.

## Phase 1 - Build New Comms in Parallel (No Cutover Yet)

Tasks:
- Implement server-side comm module under a new package (e.g., `backend/comm/`).
- Implement `ConnectionManager`, heartbeat monitor, command lifecycle tracking.
- Add client simulator capable of N concurrent virtual clients.
- Implement new client agent skeleton with registration and heartbeat.

Exit criteria:
- Simulated multi-client connectivity stable (no cross-client command routing).

## Phase 2 - Command Path Migration

Tasks:
- Implement command envelopes and ack/result flow.
- Adapt existing `/commandClient` route to call new `CommandRouter`.
- Keep old route contract so UI remains unchanged initially.

Exit criteria:
- Single real client receives and executes `step`/`display` reliably through new path.
- UI still works without major front-end changes.

## Phase 3 - Video Path Migration

Tasks:
- Add authenticated video channel keyed to session.
- Bind frames to `client_id` in `VideoFrameStore`.
- Keep `/video_feed/<client_id>` output behavior.

Exit criteria:
- Correct per-client video mapping for at least 3 concurrent clients.

## Phase 4 - Reconnect/Resilience Hardening

Tasks:
- Exponential backoff + jitter reconnect on client.
- Server session expiry and stale cleanup.
- Heartbeat timeout handling and graceful status transitions.

Exit criteria:
- Network interruption recovery within target time without manual restart.

## Phase 5 - Dual-Stack Rollout and Legacy Removal

Tasks:
- Feature flag (`COMM_STACK=new|legacy|dual`).
- Canary one client on new stack.
- Expand to all clients.
- Remove legacy socket accept pairing code after stable soak period.

Exit criteria:
- New stack is default and legacy path retired.

---

## Testing Strategy

## A) Current-Code Test Gate (Pre-Migration)

- Manual smoke on one server + one client:
  - send `step`
  - send `display`
  - start video and verify feed
- Multi-client attempt with 2+ clients to document current failures and reproduction steps.

## B) New Stack Automated Tests

- Unit tests:
  - protocol validation
  - session state transitions
  - heartbeat timeout logic
- Integration tests:
  - simulated clients register/send heartbeat/receive commands
  - command ack/result lifecycle
  - video frame routing per client
- Failure tests:
  - random disconnect/reconnect
  - duplicate `client_id`
  - delayed acks/results

## C) Hardware-in-the-loop Tests

- One real client with serial loopback or real MCU.
- Validate command execution and status reporting.
- Validate camera stream continuity over extended run.

## D) Soak Test

- 3+ clients for 60+ minutes.
- periodic commands + continuous video.
- measure command failure rate and stream mapping correctness.

---

## Acceptance Criteria (Definition of Done)

- Correct command routing for 3+ simultaneous clients.
- No cross-client command/video misassociation.
- Reconnect after transient network loss in <10s target.
- Command observability:
  - sent
  - acked/rejected
  - succeeded/failed
  all with timestamps and identifiers.
- UI workflows unchanged or clearly migrated with minimal disruption.
- Legacy sequential `accept()` pairing removed.

---

## Operational Requirements

- Add explicit runtime config (env or config file):
  - server bind host/port(s)
  - heartbeat interval + timeout
  - reconnect backoff bounds
  - duplicate client policy
  - feature flag for stack selection
- Move from hardcoded host values in `constants.py` toward environment-driven config.
- Use stable serial device names on client (`/dev/serial/by-id/...`) where possible.

---

## Risk Register

- **Risk:** Hardware not available during dev.
  - **Mitigation:** strong simulator + serial stubs.
- **Risk:** Hidden dependencies in current startup flow.
  - **Mitigation:** Phase 0 baseline with explicit observed behavior notes.
- **Risk:** UI assumes old timing behavior.
  - **Mitigation:** keep route contracts and response semantics initially.
- **Risk:** Migration stalls due large-bang cutover.
  - **Mitigation:** dual-stack with feature flags and canary rollout.

---

## Suggested Implementation Order (Concrete)

1. Create protocol schema + message validation.
2. Implement server `ConnectionManager` + heartbeat monitor.
3. Implement client simulator and pass multi-client integration tests.
4. Implement client agent control transport + command executor adapters.
5. Wire `/commandClient` to new router.
6. Implement video channel + `/video_feed` binding.
7. Add reconnect logic and soak tests.
8. Run canary and cutover.
9. Remove legacy comm code.

---

## Deliverables

- New comm design doc (this file).
- Protocol spec document and examples.
- Server comm module.
- Client agent module.
- Simulator + integration tests.
- Rollout checklist and rollback plan.
- Updated operator runbook.

---

## Immediate Next Step

Before coding migration:
- Execute the Phase 0 baseline test on current stack and capture exact behavior/failures.
- If single-client cannot run reliably, prioritize a minimal stabilization patch first, then continue migration.
```
