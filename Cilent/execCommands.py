import socket
import serial
import time
import subprocess

import constants

def turnMotor(stepSz):
	stepSz = int(stepSz)
	print(f'turning motor by {stepSz}')
	with serial.Serial(constants.MOTOR_SERIALPORT, 9600) as ser:
		time.sleep(2)
		ser.write(("step "+str(stepSz)+"\r").encode('utf-8'))

def oledPrint(command):
	command = command.split(" ", 1)
	ind = int(command[0])
	msg = command[1]
	print(f'Printing {msg} on {ind}th place on the screen')
	with serial.Serial(constants.OLED_SERIALPORT, 9600) as ser:
		time.sleep(1)
		ser.write(("display "+str(ind)+" "+msg+"\r").encode('utf-8'))
		
def startVideo():
	subprocess.run(['python3', 'videoDisplay.py'])
	
if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print(f'connecting {constants.HOST} at {constants.PORTIN}')
	sock.connect((constants.HOST, constants.PORTIN))
	print(f'Connection Successful at {constants.HOST}, port {constants.PORTIN}\n')
	
	msg = sock.recv(constants.RECV_MSG_SIZE).decode()
	while (msg != constants.ENDWORD):
		command = msg.split(' ', 1)
		if (msg != ''):
			print(f'Sever says: {msg}, command: {command}')
		
		if (command[0] == 'step'):
			print("command found")
			turnMotor(command[1])
		elif (command[0] == 'display'):
			print("command found")
			oledPrint(command[1])
		elif (command[0] == 'start_video'):
			print("command found")
			startVideo()
		else:
			print("No Valid Command Found")
				
		msg = sock.recv(constants.RECV_MSG_SIZE).decode()
	
	print(f'Sever ended messaging')
