"""
LEGACY COMMUNICATION SCRIPT.

This standalone server-side OpenCV viewer belongs to the pre-v2 video path
and is kept for fallback/archeology. Active runtime is managed by
`Server/Web Page/backend/comm/manager.py` and served via Flask routes.
"""

import cv2
import numpy as np
import socket
import sys
import struct
import constants


def receive_and_display_video(conn, cId):
    try:
        # Create window for video display
        window_name = f"Client {cId} Video Stream"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)

        while True:
            try:
                # Receive frame size first (4 bytes)
                frame_size_data = conn.recv(4)
                if not frame_size_data:
                    print(f"Server videoDisplay.py: Client {cId} disconnected")
                    break

                frame_size = int.from_bytes(frame_size_data, byteorder="big")

                # Receive frame data
                frame_data = b""
                while len(frame_data) < frame_size:
                    chunk = conn.recv(frame_size - len(frame_data))
                    if not chunk:
                        break
                    frame_data += chunk

                if len(frame_data) == frame_size:
                    # Convert received data to numpy array
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is not None:
                        # Display the frame
                        cv2.imshow(window_name, frame)
                        print(
                            f"VideoDisplay at {cId}: Frame shape: {frame.shape}  |   dtype: {frame.dtype}"
                        )
                    else:
                        print(
                            f"Server videoDisplay.py: Failed to decode frame from client {cId}"
                        )
                else:
                    print(
                        f"Server videoDisplay.py: Incomplete frame received from client {cId}"
                    )

            except Exception as e:
                print(
                    f"Server videoDisplay.py: Error receiving video from client {cId}: {e}"
                )
                break
    except Exception as e:
        print(f"Server videoDisplay.py: Error in video display for client {cId}: {e}")

    finally:
        # Clean up
        cv2.destroyAllWindows()
        print(f"Server videoDisplay.py: Video stream ended for client {cId}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        cId = "TEst"
    else:
        cId = sys.argv[1]
    print(f"Server videoDisplay.py: Starting video display for client {cId}")

    # Create socket for video connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = None

    try:
        # Bind to video port
        sock.bind(("0.0.0.0", constants.PORT_VIDEO))
        sock.listen(1)
        print(
            f"Server videoDisplay.py: Waiting for client {cId} on port {constants.PORT_VIDEO}"
        )

        # Accept connection from client
        conn, addr = sock.accept()
        print(f"Server videoDisplay.py: Connected to client {cId} at {addr}")

        # Start video display
        receive_and_display_video(conn, cId)
    except Exception as e:
        print(
            f"Server videoDisplay.py: Error setting up video connection for client {cId}: {e}"
        )

    finally:
        # Clean up socket
        if conn is not None:
            conn.close()
        sock.close()
