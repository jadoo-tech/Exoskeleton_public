import threading
import subprocess
import time

import constants

threads = []

def runTask(script):
	subprocess.run(['python3', script])
	
if __name__ == '__main__':
	for script in constants.SCRIPTS:
		thread = threading.Thread(target = runTask, args = (script,))
		thread.daemon = True  # Allows threads to exit when the main program exits
		thread.start()
		threads.append(thread)

# Keep the main thread running indefinitely
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print("Main thread interrupted. Exiting...")
