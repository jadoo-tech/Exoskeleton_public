# Socket 

HOST = '10.57.41.213'
PORTOUT = 9158
PORTIN = 1863
PORT_VIDEO = 8612
ENDWORD = 'All data sent: code12ffda33123' ### THIS MUST BE SAME WITH SERVER'S ENDWORD!! ###
STARTSEND = 'Data will be sent now: code12cjkdi94k' ### THIS MUST BE SAME WITH SERVER'S STARTSEND!! ###

CONTROL_PORT = "/dev/ttyUSB0"
CONTROL_BAUD_RATE = 9600
### File sending format:
	# 2. send the file type (extension, ex. txt if text)
	# 3. Send data/message
	# 4. send end file
	# 5. send ENDWORD when done with file sending. Otherwise repeat 2~4
	
EXTENSION_LIST = ['txt', 'csv']


##############THREADS##################
FILE_NAME = 'large'
FILE_TYPE = 'csv'
SCRIPTS = ['updateData.py', 'execCommands.py']  # List of scripts to be ran
RECV_MSG_SIZE = 1024

##############Controls##################
MOTOR_SERIALPORT = "/dev/ttyUSB0"
OLED_SERIALPORT = "/dev/ttyACM0"
