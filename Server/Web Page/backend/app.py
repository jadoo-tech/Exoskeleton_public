from flask import Flask, jsonify, render_template, request
import csv
from werkzeug.middleware.proxy_fix import ProxyFix

### CIENT PI COMMUNICATION ###
import threading
import subprocess
import time
import socket
import sys

import constants
################################

app = Flask(__name__, template_folder = '../html', static_folder='../static')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1) 

### CIENT PI COMMUNICATION ###
clients = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((constants.HOST, constants.PORTOUT))
#def runRecv(cId):
#	subprocess.run(['python3', 'recvFile.py', str(cId)])
def initialize_Connection(cId):
    sock.listen()
    print(f'Initiating port from new client')
    try:
        clients.update({cId:sock.accept()})
        print(f'Connected with client for recieving data')
    except Exception as e:
        print(e)

def sendCommand(command, cId):
    conn = clients.get(cId) 
    if (not conn):
        print("Initializing")
        initialize_Connection(cId)
        conn = clients.get(cId)
    if (command != 'stop sending'):
        print(f"Sending {command} to {cId}")
        conn[0].send(command.encode())
    else:
        conn[0].send(str(constants.ENDWORD).encode())
        conn[0].close()
        clients.pop(cId)
###############################

def read_csv():
    data = []
    with open('data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

@app.route('/commandClient', methods=['POST'])
def commandClient():
    try:
        msg = request.data.decode('utf-8').split(' on Client: ')
        print(msg, "command recieved")
        command = msg[0]
        cId = msg[1]
        if (cId):
            sendCommand(command, cId)
            return f"Command: '{command}' sent to client {cId}."
        return "Enter client id"
    except Exception as e:
        print(e)
        return f"error: {e}"

# LOADING PAGES #
@app.route('/fetchData')
def get_data():
    data = read_csv()
    return jsonify(data)
@app.route('/404Error')
def open_error_page():
    return render_template('404.html')
@app.route('/dataDisplay')
def open_data_page():
    return render_template('DataDisplay.html')
@app.route('/motionControls')
def open_controls_page():
    return render_template('MotionControl.html')
@app.route('/')
def open_home_page():
    return render_template('Home.html')

if __name__ == '__main__':
    print("Sockets Created")
    
    print("RUNNING")
    app.run(debug=True)

#### CLIENT PI ####
    #if (constants.CLIENTNUM < 1):
	#	constants.CLIENTNUM = int(input("How many clients? "))
		
    # Establishing Threads
	#for clientID in range(constants.CLIENTNUM):
	#	thread = threading.Thread(target = runRecv, args = (clientID, ))
	#	thread.daemon = True  # Allows threads to exit when the main program exits
	#	thread.start()
	#	recvThreads.append(thread)
    
    # Creating Connection For Sending Message
		
