import socket
import constants
import sys

def recvFile(cId):
	# Receiving File Data
	fInfo = conn[0].recv(1024).decode('utf-8').split(', ')
	fType = fInfo[0]
	size = int(fInfo[1])
	length = int(fInfo[2])
	conn[0].send(("Data recieved").encode())
	
	# Creating a new file at server end and writing the data 
	filename = f'Client {cId}.{fType}'
	fo = open(filename, "w")
	
	for i in range(length):
		data = conn[0].recv(size).decode()
		if (data == ''):
			break
		fo.write(data)
	print('\n Received successfully! New filename is:', filename) 
	fo.close() 

if __name__ == '__main__':
# Creating Connection
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((constants.HOST, constants.PORTIN))
	sock.listen()
	
	cId = int(sys.argv[1])
	
	print(f'Initiating recieving port from client {cId}')
	conn = sock.accept()
	print(f'Connected with client {cId} for recieving data')
	
	recvFile(cId)
	
	# Closing Connection
	conn[0].close() 
