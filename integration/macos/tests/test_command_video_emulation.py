from __future__ import annotations

import io
import json
import socket
import struct
import threading
import time
import uuid

from PIL import Image


def _connect_with_retry(
    host: str, port: int, timeout_seconds: float = 8.0
) -> socket.socket:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            return sock
        except OSError as err:
            last_error = err
            sock.close()
            time.sleep(0.05)

    raise RuntimeError(f"Timed out connecting to {host}:{port}: {last_error}")


def _send_json_line(sock: socket.socket, payload: dict) -> None:
    encoded = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
    sock.sendall(encoded)


def _read_json_line(reader) -> dict:
    line = reader.readline()
    if not line:
        raise RuntimeError("Socket closed while reading JSON line")
    return json.loads(line.decode("utf-8"))


def _jpeg_frame_bytes() -> bytes:
    frame = Image.new("RGB", (16, 16), color=(20, 120, 240))
    payload = io.BytesIO()
    frame.save(payload, format="JPEG", quality=75)
    return payload.getvalue()


def _client_emulator(
    host: str,
    command_port: int,
    video_port: int,
    client_id: str,
    received_commands: list[str],
):
    control_sock = _connect_with_retry(host, command_port)
    control_reader = control_sock.makefile("rb")

    hello = {
        "version": 1,
        "type": "hello",
        "client_id": client_id,
        "session_id": None,
        "msg_id": uuid.uuid4().hex,
        "ts": time.time(),
        "payload": {},
    }
    _send_json_line(control_sock, hello)

    hello_ack = _read_json_line(control_reader)
    session_id = hello_ack["session_id"]

    video_sock = _connect_with_retry(host, video_port)
    video_registration = {
        "version": 1,
        "type": "video_hello",
        "client_id": client_id,
        "session_id": session_id,
        "msg_id": uuid.uuid4().hex,
        "ts": time.time(),
        "payload": {},
    }
    encoded_registration = json.dumps(video_registration, separators=(",", ":")).encode(
        "utf-8"
    )
    video_sock.sendall(struct.pack(">I", len(encoded_registration)))
    video_sock.sendall(encoded_registration)

    try:
        frame = _jpeg_frame_bytes()
        video_sock.sendall(struct.pack(">I", len(frame)))
        video_sock.sendall(frame)

        command_msg = _read_json_line(control_reader)
        if command_msg.get("type") == "command":
            command = command_msg.get("payload", {}).get("command", "")
            msg_id = command_msg.get("msg_id", "")
            received_commands.append(command)

            _send_json_line(
                control_sock,
                {
                    "version": 1,
                    "type": "command_ack",
                    "client_id": client_id,
                    "session_id": session_id,
                    "msg_id": msg_id,
                    "ts": time.time(),
                    "payload": {"accepted": True},
                },
            )

            _send_json_line(
                control_sock,
                {
                    "version": 1,
                    "type": "command_result",
                    "client_id": client_id,
                    "session_id": session_id,
                    "msg_id": msg_id,
                    "ts": time.time(),
                    "payload": {"status": "ok", "detail": "emulated"},
                },
            )

        time.sleep(0.2)
    finally:
        video_sock.close()
        control_reader.close()
        control_sock.close()


def test_start_video_command_and_stream_endpoint(backend_module, backend_client):
    backend_module.connection_manager.ensure_started()

    client_id = "emu1"
    received_commands: list[str] = []

    worker = threading.Thread(
        target=_client_emulator,
        args=(
            "127.0.0.1",
            backend_module.connection_manager.control_port,
            backend_module.connection_manager.video_port,
            client_id,
            received_commands,
        ),
        daemon=True,
    )
    worker.start()

    deadline = time.time() + 5
    while True:
        clients = backend_module.connection_manager.list_clients()
        if any(client["client_id"] == client_id for client in clients):
            break
        if time.time() > deadline:
            raise RuntimeError("Client did not register in time")
        time.sleep(0.05)

    response = backend_client.post(
        "/commandClient",
        data=f"start_video on Client: {client_id}",
        content_type="text/plain",
    )

    assert response.status_code == 200
    assert f"sent to client {client_id}" in response.get_data(as_text=True)

    deadline = time.time() + 5
    while backend_module.connection_manager.get_latest_frame(client_id) is None:
        if time.time() > deadline:
            raise RuntimeError("Frame did not arrive in time")
        time.sleep(0.05)

    deadline = time.time() + 5
    while not received_commands and time.time() < deadline:
        time.sleep(0.05)

    assert any("start_video" in cmd for cmd in received_commands)

    stream_response = backend_client.get(f"/video_feed/{client_id}")
    assert stream_response.status_code == 200

    worker.join(timeout=1.0)
