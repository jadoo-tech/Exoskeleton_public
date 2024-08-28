import socket
import sys
import constants

cId = 0 	#DELETE THIS LINE

if __name__ == '__main__':
	# Creating Connection
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((constants.HOST, constants.PORTOUT))
	sock.listen()
	
	#cId = int(sys.argv[1])
	
	print(f'Initiating recieving port from client')
	conn = sock.accept()
	print(f'Connected with client {cId} for recieving data')
	
	msg = input("Type in your message. Type 'stop sending' to stop: ").lower()
	while (msg != 'stop sending'):
		conn[0].send(msg.encode())
		msg = input("Type in your message. Type 'stop sending' to stop: ").lower()
	conn[0].send(str(constants.ENDWORD).encode())
	
	# Closing Connection
	conn[0].close() 
