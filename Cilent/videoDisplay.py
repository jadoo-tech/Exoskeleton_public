import io
import os
import socket
import struct
import sys
import time

from PIL import Image

import constants

try:
    from picamera2 import Picamera2  # type: ignore[import-not-found]
except Exception:
    Picamera2 = None


SIM_MODE = os.getenv("EXO_SIM_MODE", "0") == "1"


def connect_with_retry(host, port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Connecting to server at {host}:{port} for video")
            sock.connect((host, port))
            print(f"Connected to {host}:{port} for video")
            return sock
        except OSError as err:
            sock.close()
            print(f"Video socket connect failed: {err}. Retrying in 1s")
            time.sleep(1)


def frame_from_camera(picam2):
    stream = io.BytesIO()
    array = picam2.capture_array()
    img = Image.fromarray(array)
    img.save(stream, format="JPEG", quality=70)
    return stream.getvalue()


def frame_from_simulation(frame_count):
    stream = io.BytesIO()
    color = (frame_count % 255, 80, 220)
    img = Image.new("RGB", (640, 480), color=color)
    img.save(stream, format="JPEG", quality=70)
    return stream.getvalue()


def send_video_stream(sock, cId):
    print("Video stream loop started")
    use_camera = Picamera2 is not None and not SIM_MODE
    picam2 = None

    if use_camera and Picamera2 is not None:
        picam2 = Picamera2()
        config = picam2.create_still_configuration(
            main={"size": (640, 480)}, buffer_count=1
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(2)
    else:
        use_camera = False
        print("SIM_MODE or no picamera2 detected: sending synthetic frames")

    try:
        frame_count = 0
        while True:
            if use_camera:
                frame_data = frame_from_camera(picam2)
            else:
                frame_data = frame_from_simulation(frame_count)

            sock.sendall(struct.pack(">I", len(frame_data)))
            sock.sendall(frame_data)

            frame_count += 1
            if frame_count % 30 == 0:
                print(f"Sent {frame_count} frames (Client: {cId})")

            time.sleep(1 / 15)
    except KeyboardInterrupt:
        print("Video streaming stopped by user")
    except Exception as e:
        print(f"Error in video streaming: {e}")
    finally:
        if picam2 is not None:
            picam2.close()
        print(f"Video streaming ended (Client: {cId})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 videoDisplay.py <client_id>")
        cId = "TestId"
    else:
        cId = sys.argv[1]

    time.sleep(1)
    sock = connect_with_retry(constants.HOST, constants.PORT_VIDEO)
    try:
        send_video_stream(sock, cId)
    finally:
        sock.close()
