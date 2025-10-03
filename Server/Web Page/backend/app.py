from flask import Flask, jsonify, render_template, request, Response, abort
import csv
from werkzeug.middleware.proxy_fix import ProxyFix

#### DISPLAY ####
import cv2
import numpy as np
##################


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

latest_frames = {}  # Store latest frame for each client

### CIENT PI COMMUNICATION ###
clients_exec = {}
clients_video = {}
sock_exec = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_exec.bind((constants.HOST, constants.PORTOUT))
sock_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_video.bind((constants.HOST, constants.PORT_VIDEO))


def initialize_Connection(cId):
    #subprocess.run(['python3', 'recvFile.py', str(cId)])
    try:
        sock_exec.listen(1)
        print(f'Initiating port from new client at {constants.PORTOUT}')
        clients_exec.update({cId:sock_exec.accept()})
        print(f'Connected with client {cId} to send commands')

        sock_video.listen(1)
        print(f'Initiating port from new client at {constants.PORT_VIDEO}')
        clients_video.update({cId:sock_video.accept()})
        print(f'Connected with client {cId} to recieve video')

        threading.Thread(target=receive_frames, args=(cId,)).start()
    except Exception as e:
        print(e)
    
def receive_frames(vId):
    global latest_frames
    conn_video = clients_video.get(vId)[0]
    print(f"Recieving video from {vId}, conn: {conn_video}")
    while True:
        # Receive frame size
        frame_size_data = conn_video.recv(4)
        if not frame_size_data:
            break
        frame_size = int.from_bytes(frame_size_data, byteorder='big')
        # Receive frame data
        frame_data = b''
        while len(frame_data) < frame_size:
            chunk = conn_video.recv(frame_size - len(frame_data))
            if not chunk:
                break
            frame_data += chunk
        if len(frame_data) == frame_size:
            latest_frames.update({vId:frame_data})
            print(f"Received frame from {vId}")
            
###############################
def gen(cId):
    while True:
        frame = latest_frames.get(cId)
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(1/15)

def read_csv():
    data = []
    with open('data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

@app.route('/video_feed/<vId>')
def displayVideo(vId):
    print(f"Displaying video for {vId}")
    if vId not in latest_frames:
        return abort(404, description=f"No video stream for client {vId}")
    return Response(gen(vId), mimetype='multipart/x-mixed-replace; boundary=frame')

def sendCommand(command, cId):
    conn = clients_exec.get(cId) 
    if (not conn):
        print("Initializing")
        initialize_Connection(cId)
        conn = clients_exec.get(cId)

    if (command != 'stop sending'):
        print(f"Sending {command} to {cId}")
        conn[0].send(command.encode())
    else:
        print(f"Closing connection with {cId}")
        conn[0].send(str(constants.ENDWORD).encode())
        conn[0].close()
        clients_exec.pop(cId)

@app.route('/commandClient', methods=['POST'])
def commandClient():
    try:
        msg = request.data.decode('utf-8').split(' on Client: ')
        print(msg, "command recieved")
        command = msg[0]
        cId = msg[1]
        if (command == 'start_video'):
            if (cId not in clients_video):
                sendCommand(command, cId)
            print(f"Video for {cId} requested")
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

@app.route('/video_feed/<client_id>')
def video_feed(client_id):
    if client_id not in latest_frames:
        # Optionally, wait for the first frame or return 404
        return abort(404, description=f"No video stream for client {client_id}")
    return Response(gen(client_id), mimetype='multipart/x-mixed-replace; boundary=frame')

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
		
