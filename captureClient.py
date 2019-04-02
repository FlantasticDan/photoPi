#!/usr/bin/env python3

# controls individual pis locally based on LAN commands

import socket
import sys
import os
import time
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
FILE_NAME = str(socket.gethostname()) + "_" + fileName
msgSend(FILE_NAME) # debug
imgFormat = msgDecode()
msgSend(imgFormat) # debug

def cameraCalibration(iso=0, shutter=0):
    camera.start_preview()
    camera.iso = iso
    camera.shutter_speed = shutter
    camera.exposure_mode = 'auto'
    camera.awb_mode = "auto"
    time.sleep(2) # pause for exposure adjustments
    camera.exposure_mode = 'off'
    time.sleep(0.25) # allow white balance to adjust based on locked exposure
    whiteBal = camera.awb_gains
    camera.awb_mode = "off"
    time.sleep(0.25) # allow gains to settle
    camera.awb_gains = whiteBal
    camera.stop_preview()

def profileAnnotation(profile):
    string = '''PROFILE {}\nShutter: {:.3f} ISO: {}\nGain: {:.3f} :: {:.3f}
    White Balance: {:.3f} :: {:.3f}'''.format(profile, camera.exposure_speed * 0.000001,
        camera.iso, float(camera.digital_gain), float(camera.analog_gain),
        float(camera.awb_gains[0]), float(camera.awb_gains[1]))
    return string

def generateProfiles():
    path = fileName + "_Profiles"
    os.mkdir(path, 0o777)
    cameraCalibration()
    camera.annotate_text = profileAnnotation(1)
    camera.capture("{}/1.jpeg".format(path))
    cameraCalibration(100)
    camera.annotate_text = profileAnnotation(2)
    camera.capture("{}/2.jpeg".format(path))
    cameraCalibration(100, 10000)
    camera.annotate_text = profileAnnotation(3)
    camera.capture("{}/3.jpeg".format(path))
    cameraCalibration(200, 10000)
    camera.annotate_text = profileAnnotation(4)
    camera.capture("{}/4.jpeg".format(path))
    cameraCalibration(400, 10000)
    camera.annotate_text = profileAnnotation(5)
    camera.capture("{}/5.jpeg".format(path))
    camera.annotate_text = ""


# generate exposure profiles
msg = msgDecode()
if msg == "EXPOSURE":
    generateProfiles()
    msgSend("GENERATED")
    msg = msgDecode()
