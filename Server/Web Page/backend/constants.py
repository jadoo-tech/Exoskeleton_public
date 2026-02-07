# Defining Socket

import os


HOST = os.getenv("EXO_HOST", "10.57.43.134")
PORTIN = 9158  # This has to be kept same with client's PORTOUT #
PORTOUT = 1863  # This has to be kept same with client's PORTIN #
PORT_VIDEO = 8612  # This has to be kept same with client's PORT_VIDEO #

COMM_STACK = os.getenv("EXO_COMM_STACK", "v2")
PROTOCOL_VERSION = 1

HEARTBEAT_INTERVAL_S = float(os.getenv("EXO_HEARTBEAT_INTERVAL_S", "5"))
HEARTBEAT_TIMEOUT_S = float(os.getenv("EXO_HEARTBEAT_TIMEOUT_S", "20"))
VIDEO_STREAM_FPS = float(os.getenv("EXO_VIDEO_STREAM_FPS", "15"))
MAX_FRAME_BYTES = int(os.getenv("EXO_MAX_FRAME_BYTES", "4000000"))
MAX_CONTROL_LINE_BYTES = int(os.getenv("EXO_MAX_CONTROL_LINE_BYTES", "65536"))

CLIENTNUM = 1  ##### TODO: Implement mulitple connection #####
ENDWORD = "All data sent: code12ffda33123"  ### THIS MUST BE SAME WITH THE CLIENTS'S ENDWORD!! ###
STARTSEND = "Data will be sent now: code12cjkdi94k"  ### THIS MUST BE SAME WITH CLIENTS'S STARTSEND!! ###

### THREAD CONSTANTS ###


## TODOS ##
# Have to find a way to create files in a sub folder when receiving data
