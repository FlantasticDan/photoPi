#!/usr/bin/env python3

# controls individual pis locally based on LAN commands

import socket
import sys
import picamera

# server connection and client identification
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.connect((sys.argv[1], int(sys.argv[2])))

# utf-8 byte encoder with injected header
def msgEncode(message):
    msg = str(message)
    msgLength = len(msg)
    msg = "{:<4}".format(msgLength) + msg
    msg = msg.encode()
    return msg

# utf-8 byte reciever, buffer, and decoder
def msgDecode():
    chunk = SERVER.recv(1)
    while len(chunk) < 4:
        chunk += SERVER.recv(1)
    chunk = chunk.decode()
    msgLength = int(chunk[:4])
    msg = chunk[4:]
    while len(msg) < msgLength:
        chunk = SERVER.recv(1)
        chunk = chunk.decode()
        msg += chunk
    return msg

# send encoded message to server
def msgSend(message):
    msg = msgEncode(message)
    SERVER.send(msg)

msgSend(socket.gethostname())

# calibrate camera
camera = picamera.PiCamera()
camera.resolution = (3280, 2464)
camera.meter_mode = 'spot'
camera.image_denoise = False

fileName = msgDecode()
fileName = str(socket.gethostname()) + "_" + fileName
msgSend(fileName) # debug
imgFormat = msgDecode()
msgSend(imgFormat) # debug
