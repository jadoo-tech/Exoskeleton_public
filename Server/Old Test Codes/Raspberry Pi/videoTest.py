import socket
import cv2
import numpy as np
import constants

def display_video():
    # Initialize a socket to listen for incoming connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((constants.HOST, constants.PORTIN))
        server_socket.listen(1)
        connection, _ = server_socket.accept()

        with connection:
            # Create an OpenCV window
            cv2.namedWindow("Video Feed", cv2.WINDOW_AUTOSIZE)
           
            while True:
                # Read the length of the incoming frame
                length_data = connection.recv(4)
                if not length_data:
					print("No data input")
                    break
               
                length = int.from_bytes(length_data, 'big')
               
                # Read the frame data
                frame_data = b''
                while len(frame_data) < length:
                    frame_data += connection.recv(length - len(frame_data))
               
                # Convert the frame data to an image
                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
               
                # Display the frame
                if frame is not None:
                    cv2.imshow("Video Feed", frame)
               
                # Exit if 'q' key is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Cleanup
            cv2.destroyAllWindows()

if __name__ == "__main__":
    display_video()
