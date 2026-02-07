# Socket

import os
import socket


HOST = os.getenv("EXO_HOST", "10.57.43.134")
PORTOUT = 9158
PORTIN = 1863
PORT_VIDEO = 8612

COMM_STACK = os.getenv("EXO_COMM_STACK", "v2")
PROTOCOL_VERSION = 1
CLIENT_ID = os.getenv("EXO_CLIENT_ID", socket.gethostname())

ENDWORD = (
    "All data sent: code12ffda33123"  ### THIS MUST BE SAME WITH SERVER'S ENDWORD!! ###
)
STARTSEND = "Data will be sent now: code12cjkdi94k"  ### THIS MUST BE SAME WITH SERVER'S STARTSEND!! ###

HEARTBEAT_INTERVAL_S = float(os.getenv("EXO_HEARTBEAT_INTERVAL_S", "5"))
HEARTBEAT_TIMEOUT_S = float(os.getenv("EXO_HEARTBEAT_TIMEOUT_S", "20"))
CONNECT_RETRY_S = float(os.getenv("EXO_CONNECT_RETRY_S", "1"))
VIDEO_FPS = float(os.getenv("EXO_VIDEO_FPS", "15"))
MAX_CONTROL_LINE_BYTES = int(os.getenv("EXO_MAX_CONTROL_LINE_BYTES", "65536"))

### File sending format:
# 2. send the file type (extension, ex. txt if text)
# 3. Send data/message
# 4. send end file
# 5. send ENDWORD when done with file sending. Otherwise repeat 2~4

EXTENSION_LIST = ["txt", "csv"]

##############THREADS##################
FILE_NAME = "large"
FILE_TYPE = "csv"
SIM_MODE = os.getenv("EXO_SIM_MODE", "0") == "1"

# Legacy (pre-v2) scripts kept for fallback/archeology.
LEGACY_SCRIPTS = ["updateData.py", "execCommands.py", "videoDisplay.py"]
if SIM_MODE:
    LEGACY_SCRIPTS = ["execCommands.py", "videoDisplay.py"]

SCRIPTS = ["agent.py"] if COMM_STACK == "v2" else LEGACY_SCRIPTS
RECV_MSG_SIZE = 1024

##############Controls##################
MOTOR_SERIALPORT = "/dev/ttyUSB0"
OLED_SERIALPORT = "/dev/ttyACM0"
CONTROL_PORT = "/dev/ttyUSB0"
CONTROL_BAUD_RATE = 9600
