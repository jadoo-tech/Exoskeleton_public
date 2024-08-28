import socket
import constants

if __name__ == '__main__': 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	sock.bind((constants.HOST, constants.PORT))
	if constants.CLIENTNUM <= 0:
		constants.CLIENTNUM = int(input('Enter number of clients: ')) 
	sock.listen(constants.CLIENTNUM)
	
	print(constants.PORT)
	
	# Establishing Connections 
	connections = [] 
	print('Initiating clients') 
	for i in range(constants.CLIENTNUM):
		print('enterd for loop')
		conn = sock.accept() 
		print('accepted')
		connections.append(conn) 
		print('Connected with client', i+1) 

	fileno = 0
	idx = 0
	for conn in connections: 
		# Receiving File Data 
		idx += 1
		data = conn[0].recv(1024).decode() 

		if not data: 
			continue
	# Creating a new file at server end and writing the data 
		filename = 'Recieved_file'+str(fileno)+'.txt'
		fileno = fileno+1
		fo = open(filename, "w") 
		while data: 
			if not data: 
				break
			else: 
				fo.write(data) 
				data = conn[0].recv(1024).decode() 

		print() 
		print('Receiving file from client', idx) 
		print() 
		print('Received successfully! New filename is:', filename) 
		fo.close() 
	# Closing all Connections 
	for conn in connections: 
		conn[0].close() 
