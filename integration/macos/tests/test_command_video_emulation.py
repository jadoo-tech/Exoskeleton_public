from __future__ import annotations

import io
import socket
import struct
import threading
import time

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


def _jpeg_frame_bytes() -> bytes:
    frame = Image.new("RGB", (16, 16), color=(20, 120, 240))
    payload = io.BytesIO()
    frame.save(payload, format="JPEG", quality=75)
    return payload.getvalue()


def _client_emulator(
    host: str, command_port: int, video_port: int, received_commands: list[str]
) -> None:
    command_sock = _connect_with_retry(host, command_port)
    video_sock = _connect_with_retry(host, video_port)

    try:
        command_sock.settimeout(1.5)

        try:
            first = command_sock.recv(1024).decode("utf-8")
            if first:
                received_commands.append(first)
        except socket.timeout:
            pass

        try:
            second = command_sock.recv(1024).decode("utf-8")
            if second:
                received_commands.append(second)
        except socket.timeout:
            pass

        frame = _jpeg_frame_bytes()
        video_sock.sendall(struct.pack(">I", len(frame)))
        video_sock.sendall(frame)
        time.sleep(0.2)
    finally:
        command_sock.close()
        video_sock.close()


def test_start_video_command_and_stream_endpoint(backend_module, backend_client):
    client_id = "emu1"
    received_commands: list[str] = []

    worker = threading.Thread(
        target=_client_emulator,
        args=("127.0.0.1", 1863, 8612, received_commands),
        daemon=True,
    )
    worker.start()

    response = backend_client.post(
        "/commandClient",
        data=f"start_video on Client: {client_id}",
        content_type="text/plain",
    )

    assert response.status_code == 200
    assert f"sent to client {client_id}" in response.get_data(as_text=True)

    deadline = time.time() + 5
    while client_id not in backend_module.latest_frames and time.time() < deadline:
        time.sleep(0.05)

    assert client_id in backend_module.latest_frames
    assert any("start_video" in cmd for cmd in received_commands)

    stream_response = backend_client.get(f"/video_feed/{client_id}")
    assert stream_response.status_code == 200

    worker.join(timeout=1.0)
