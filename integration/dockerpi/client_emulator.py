from __future__ import annotations

import argparse
import io
import socket
import struct
import sys
import time

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emulate the exoskeleton client command/video protocol"
    )
    parser.add_argument("--host", required=True, help="Server host/IP")
    parser.add_argument("--command-port", type=int, default=1863)
    parser.add_argument("--video-port", type=int, default=8612)
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--max-seconds", type=int, default=300)
    return parser.parse_args()


def connect_with_retry(
    host: str, port: int, timeout_seconds: float = 40.0
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
            time.sleep(0.25)

    raise RuntimeError(f"Unable to connect to {host}:{port}: {last_error}")


def jpeg_frame(counter: int) -> bytes:
    image = Image.new("RGB", (160, 120), color=(counter % 255, 40, 220))
    payload = io.BytesIO()
    image.save(payload, format="JPEG", quality=75)
    return payload.getvalue()


def main() -> int:
    args = parse_args()
    print(f"Connecting command socket to {args.host}:{args.command_port}", flush=True)
    command_sock = connect_with_retry(args.host, args.command_port)
    print(f"Connecting video socket to {args.host}:{args.video_port}", flush=True)
    video_sock = connect_with_retry(args.host, args.video_port)

    command_sock.settimeout(0.5)

    start = time.time()
    counter = 0
    try:
        while time.time() - start < args.max_seconds:
            try:
                message = command_sock.recv(1024)
                if message:
                    print(
                        f"SERVER COMMAND: {message.decode('utf-8', errors='replace')}",
                        flush=True,
                    )
            except socket.timeout:
                pass

            frame = jpeg_frame(counter)
            video_sock.sendall(struct.pack(">I", len(frame)))
            video_sock.sendall(frame)
            counter += 1
            time.sleep(max(0.01, 1.0 / args.fps))
    finally:
        command_sock.close()
        video_sock.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
