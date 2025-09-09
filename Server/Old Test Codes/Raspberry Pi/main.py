import threading
import subprocess
import time
import socket
import pickle

import constants

recvThreads = []
sendThreads = []

def runRecv(cId):
	subprocess.run(['python3', 'recvFile.py', str(cId)])
	
def runSend(cId):
	subprocess.run(['python3', 'sendMsg.py', str(cId)])
	
if __name__ == '__main__':
	if (constants.CLIENTNUM < 1):
		constants.CLIENTNUM = int(input("How many clients? "))
		
	# Establishing Threads
	for clientID in range(constants.CLIENTNUM):
		thread = threading.Thread(target = runRecv, args = (clientID, ))
		thread.daemon = True  # Allows threads to exit when the main program exits
		thread.start()
		recvThreads.append(thread)
		
		thread = threading.Thread(target = runSend, args = (clientID, ))
		thread.daemon = True  # Allows threads to exit when the main program exits
		thread.start()
		sendThreads.append(thread)

# Keep the main thread running indefinitely
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print("Main thread interrupted. Exiting...")
