"""
LEGACY COMMUNICATION SCRIPT.

This file belongs to the pre-v2 client command path and is kept for
fallback/archeology. Active runtime uses `Cilent/agent.py` when
`EXO_COMM_STACK=v2`.
"""

import os
import socket
import time

import serial

import constants


SIM_MODE = os.getenv("EXO_SIM_MODE", "0") == "1"


def connect_with_retry(host, port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Connecting {host}:{port} to receive commands")
            sock.connect((host, port))
            print(f"Connected to {host}:{port} for commands")
            return sock
        except OSError as err:
            sock.close()
            print(f"Command socket connect failed: {err}. Retrying in 1s")
            time.sleep(1)


def turnMotor(stepSz):
    stepSz = int(stepSz)
    print(f"Turning motor by {stepSz}")

    if SIM_MODE:
        print("SIM_MODE: skipping motor serial write")
        return

    with serial.Serial(constants.MOTOR_SERIALPORT, 9600) as ser:
        time.sleep(2)
        ser.write(("step " + str(stepSz) + "\r").encode("utf-8"))


def oledPrint(command):
    command = command.split(" ", 1)
    ind = int(command[0])
    msg = command[1]
    print(f"Printing {msg} on index {ind}")

    if SIM_MODE:
        print("SIM_MODE: skipping OLED serial write")
        return

    with serial.Serial(constants.OLED_SERIALPORT, 9600) as ser:
        time.sleep(1)
        ser.write(("display " + str(ind) + " " + msg + "\r").encode("utf-8"))


if __name__ == "__main__":
    sock = connect_with_retry(constants.HOST, constants.PORTIN)

    while True:
        data = sock.recv(constants.RECV_MSG_SIZE)
        if not data:
            print("Server closed command socket")
            break

        msg = data.decode()
        if msg == constants.ENDWORD:
            print("Server ended messaging")
            break

        if msg:
            command = msg.split(" ", 1)
            print(f"Server says: {msg}, command: {command}")

            if command[0] == "step" and len(command) > 1:
                turnMotor(command[1])
            elif command[0] == "display" and len(command) > 1:
                oledPrint(command[1])
            elif command[0] == "start_video":
                print("start_video command received")
            else:
                print("No valid command found")

    sock.close()
