import socket
import constants

def recieveFileAt(extension, size, filename, client_num):
# Creating a new file at server end and writing the data 
	fo = open(filename+'.'+extension, "w")
# Receiving File Data
	datas = conn[client_num].recv(size).decode()
	for data in datas:
		fo.write(data)
	print('Received successfully! New filename is:', filename) 
	fo.close()

if __name__ == '__main__': 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	sock.bind((constants.HOST, constants.PORT))
	if constants.CLIENTNUM <= 0:
		constants.CLIENTNUM = int(input('Enter number of clients: ')) 
	sock.listen(constants.CLIENTNUM)
	
	# Establishing Connections 
	connections = [] 
	print('Initiating clients') 
	for i in range(constants.CLIENTNUM):
		conn = sock.accept()
		connections.append(conn) 
		print('Connected with client', i+1)
		print()
		
	fileno = 0
	idx = 0
	for conn in connections:
		print('Receiving file from client', (idx+1))
		while True:  # Recieving data
			extension = conn[idx].recv(1024).decode()
			print(f'extension: {extension}')
			if (extension != constants.ENDWORD):
				size = int(conn[idx].recv(1024).decode())
				print(size)
				print()
				filename = 'File'+str(idx+1)+'_'+str(fileno)
				recieveFileAt(extension, size, filename, idx)
				fileno += 1
			else:
				break
		print(f'Data recieved from {idx+1} \n')
		
		sendmsg = input("type Y if you want to send message. \nOther key to end: ").lower() == 'y'
		if sendmsg:
			conn[0].send(str(constants.STARTSEND).encode())
			msg = input("Type in message. Leave it blank to exit: ")
			while (msg != ''):
				conn[0].send(str(msg).encode())
				msg = input("Type in message. Leave it blank to exit: ")
			
		conn[0].send(str(constants.ENDWORD).encode())
		print("Messaging Ended.")
			
		# Updating indexes
		idx += 1
		fileno = 0
		
	# Closing all Connections 
	for conn in connections: 
		conn[0].close() 
