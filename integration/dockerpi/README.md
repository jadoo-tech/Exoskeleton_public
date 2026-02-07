# dockerpi Integration Harness

This setup spins up two Raspberry Pi VMs (inside Docker) so we can test server/client separation in a Pi-like environment.

## Current status

- dockerpi end-to-end tests are not working yet on this machine.
- Current blocker: VM boot reaches inconsistent state and SSH login is timing out, so payload push/start scripts cannot complete reliably.
- Treat this harness as work-in-progress until this is resolved.

It uses:

- Upstream image: `lukechilds/dockerpi`
- Patched entrypoint to support extra QEMU host forwards
- One VM for server (`server-pi`)
- One VM for client emulation (`client-pi`)

## Prerequisites

- Docker + docker-compose installed locally.
- Enough disk for two Raspberry Pi VM filesystems.

## Start/Stop

```bash
integration/dockerpi/scripts/up.sh
integration/dockerpi/scripts/down.sh
```

## Workflow

1. Start both VMs.
2. Wait until SSH is reachable (`6022` for server VM, `7022` for client VM).
3. Push runtime payload:

```bash
integration/dockerpi/scripts/push_runtime.sh
```

If you have `sshpass` installed, you can run non-interactively with:

```bash
DOCKERPI_PASSWORD=raspberry integration/dockerpi/scripts/push_runtime.sh
```

4. Start server process inside server VM:

```bash
integration/dockerpi/scripts/run_server.sh
```

5. Start client emulator inside client VM:

```bash
integration/dockerpi/scripts/run_client_emulator.sh
```

6. From host, hit server UI:

```bash
open http://localhost:18000
```

7. Use Motion Controls and issue `start_video on Client: emu1`.

## SSH helper scripts

```bash
integration/dockerpi/scripts/ssh_server.sh
integration/dockerpi/scripts/ssh_client.sh
```

## Notes and constraints

- This validates network protocol and backend behavior, not physical hardware behavior.
- The emulator replaces motor/OLED/camera hardware in the client VM.
- If you want to run the real `Cilent/main.py` in the client VM, serial and camera dependencies will still fail without physical devices.
- Default dockerpi credentials are `pi` / `raspberry`.
- Scripts support `DOCKERPI_USER` and `DOCKERPI_PASSWORD` env vars.
