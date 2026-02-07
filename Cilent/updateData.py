"""
LEGACY COMMUNICATION SCRIPT.

This file belongs to the pre-v2 client data-upload path and is kept for
fallback/archeology. It is not part of the active v2 runtime launched by
`Cilent/main.py`.
"""

import os
import socket

import constants


def sendData(fName, fType):
    fName = fName + "." + fType
    size = os.path.getsize(fName)
    fi = open(fName, "r")
    datas = fi.readlines()

    # Send document information
    sock.send(
        (constants.FILE_TYPE + ", " + str(size) + ", " + str(len(datas))).encode()
    )
    print(f"Server says: {sock.recv(1024).decode()}")

    # Send data
    for data in datas:
        sock.send((data).encode())


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"connecting {constants.HOST} at {constants.PORTOUT} to send data\n")
    sock.connect((constants.HOST, constants.PORTOUT))
    print(
        f"Connection Successful at {constants.HOST}, port {constants.PORTOUT} to send data\n"
    )

    sendData(constants.FILE_NAME, constants.FILE_TYPE)
