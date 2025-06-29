import socket
import struct
import constants
import sys
import time
from picamera2 import Picamera2
import io
from PIL import Image

def send_video_stream(sock, cId):
    # Initialize Picamera2
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={'size': (640, 480)}, buffer_count=1)
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # Camera warm-up

    try:
        frame_count = 0
        while True:
            # Capture frame as JPEG to memory buffer
            stream = io.BytesIO()
            array = picam2.capture_array()
            # Encode as JPEG
            img = Image.fromarray(array)
            img.save(stream, format='JPEG', quality=70)
            frame_data = stream.getvalue()
            frame_size = len(frame_data)

            try:
                # Send frame size first (4 bytes, big-endian)
                sock.send(struct.pack('>I', frame_size))
                # Send frame data
                sock.send(frame_data)
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Client videoDisplay.py: Sent {frame_count} frames (Client: {cId})")
            except Exception as e:
                print(f"Client videoDisplay.py: Error sending frame: {e}")
                break
            # Small delay to control frame rate
            time.sleep(1/15)  # 15 FPS
    except KeyboardInterrupt:
        print("Client videoDisplay.py: Video streaming stopped by user")
    except Exception as e:
        print(f"Client videoDisplay.py: Error in video streaming: {e}")
    finally:
        picam2.close()
        print(f"Client videoDisplay.py: Video streaming ended (Client: {cId})")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 videoDisplay.py <client_id>")
        cId = 'TestId'
    else:
        cId = sys.argv[1]
    print(f"Client videoDisplay.py: Starting video stream to server (Client: {cId})")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"Client videoDisplay.py: Connecting to server at {constants.HOST}:{constants.PORT_VIDEO}")
        sock.connect((constants.HOST, constants.PORT_VIDEO))
        print(f"Client videoDisplay.py: Connected to server for video streaming (Client: {cId})")
        send_video_stream(sock, cId)
    except Exception as e:
        print(f"Client videoDisplay.py: Error connecting to server: {e}")
    finally:
        sock.close() 