# Integration Test Workspace

This directory is the working area for bring-up and emulation tests.

- `macos/`: local smoke tests that run on macOS without Raspberry Pi hardware.
- `dockerpi/`: Raspberry Pi VM harness using `lukechilds/dockerpi` for server/client split tests.

Note: dockerpi end-to-end tests are currently not working yet; see `integration/dockerpi/README.md` for blocker details.

Suggested flow:

1. Run macOS emulation tests first.
2. Bring up dockerpi pair.
3. Push runtime payload.
4. Start server VM process and client emulator VM process.
5. Verify command/video endpoints from host.
