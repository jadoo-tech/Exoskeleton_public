import os
import socket
import serial
import time

import constants

def sendText(msg):
	### DELETE (FOR DEBUGGING) ###
	print(f'sent {msg}\n')
	if (msg == constants.ENDWORD):
		print('ENDWORD SENT')
	##############################
	sock.send(str(msg).encode())

def fileSend(fType, fName):
	fName = fName+'.'fType
	try:
		fi = open(fName, 'r')
	except  IOError:
		print('Invalid file')
		return
	
	size = os.path.getsize(fName)
	

if __name__ == '__main__':
### Connecting to Server ###
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((constants.HOST, constants.PORT))
	print(f'Connection Successful at {constants.HOST}, port {constants.PORT}\n')
	
### Sending data ###
	while True:
		sendMode = input('Select file type to send. Enter: \n F to send file \n M to send message \n E to exit \n').lower()
		if len(sendMode) != 1:
			print("Length must be 1")
		elif sendMode == 'f':
			fType = input('Input file type you are going to send \n(ex: txt if a text file): ')
			fName = input('Input filename you want to send: ')
			fileSend(fType, fName)
		elif sendMode == 'm':
			msg = input('Input message ou want to send: ')
			sendText(msg+'\n')
		elif sendType == 'e':
			sendText(constants.ENDWORD)
			break
		else:
			print('invalid input')
	print('Data Sending mode escaped')

### Recieving Data ###
	msgServer = sock.recv(1024)
