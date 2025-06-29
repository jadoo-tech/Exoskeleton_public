import cv2
import numpy as np
import socket
import struct
import constants
import sys

def send_video_stream(sock, cId):
    # Initialize camera
    cap = cv2.VideoCapture(0)  # Use default camera (0)
    if not cap.isOpened():
        print("Client videoDisplay.py: Error: Could not open camera")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)  # 15 FPS for better network performance
    
    try:
        frame_count = 0
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Client videoDisplay.py: Error: Could not read frame from camera")
                break
            
            # Resize frame for better network performance
            frame = cv2.resize(frame, (640, 480))
            
            # Encode frame as JPEG with compression
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # 70% quality for better compression
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                print("Client videoDisplay.py: Error: Could not encode frame")
                continue
            
            # Get frame data
            frame_data = buffer.tobytes()
            frame_size = len(frame_data)
            
            try:
                # Send frame size first (4 bytes, big-endian)
                sock.send(struct.pack('>I', frame_size))
                
                # Send frame data
                sock.send(frame_data)
                
                frame_count += 1
                if frame_count % 30 == 0:  # Print status every 30 frames
                    print(f"Client videoDisplay.py: Sent {frame_count} frames (Client: {cId})")
                    
            except Exception as e:
                print(f"Client videoDisplay.py: Error sending frame: {e}")
                break
            
            # Optional: Add small delay to control frame rate
            cv2.waitKey(33)  # ~30 FPS (1000ms / 30fps = 33ms)
            
    except KeyboardInterrupt:
        print("Client videoDisplay.py: Video streaming stopped by user")
    except Exception as e:
        print(f"Client videoDisplay.py: Error in video streaming: {e}")
    finally:
        # Clean up camera
        cap.release()
        cv2.destroyAllWindows()
        print(f"Client videoDisplay.py: Video streaming ended (Client: {cId})")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 videoDisplay.py <client_id>")
        sys.exit(1)
    
    cId = sys.argv[1]  # Accept cId as string
    print(f"Client videoDisplay.py: Starting video stream to server (Client: {cId})")
    
    # Create socket connection to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server's video port
        print(f"Client videoDisplay.py: Connecting to server at {constants.HOST}:{constants.PORT_VIDEO}")
        sock.connect((constants.HOST, constants.PORT_VIDEO))
        print(f"Client videoDisplay.py: Connected to server for video streaming (Client: {cId})")
        
        # Start video streaming
        send_video_stream(sock, cId)
        
    except Exception as e:
        print(f"Client videoDisplay.py: Error connecting to server: {e}")
    finally:
        # Clean up socket
        sock.close() 