import os
import socket

import constants

def sendData(fName, fType):
	fName = fName+'.'+fType
	size = os.path.getsize(fName)
	fi = open(fName, 'r')
	datas = fi.readlines()
	
	# Send document information
	sock.send((constants.FILE_TYPE+', '+str(size)+', '+str(len(datas))).encode())
	print(f'Server says: {sock.recv(1024).decode()}')
	
	# Send data
	for data in datas:
		sock.send((data).encode())

if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((constants.HOST, constants.PORTOUT))
	print(f'Connection Successful at {constants.HOST}, port {constants.PORTOUT}\n')
	
	sendData(constants.FILE_NAME, constants.FILE_TYPE)
	
