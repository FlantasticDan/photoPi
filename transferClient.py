#!/usr/bin/env python3

# packages and transfers photos to serverPi

import socket
import sys
import os
import time
import shutil

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

msgSend(socket.gethostname()) # confirm connection to server with host name

# recieve target directory and confirm it exists
location = msgDecode()
isDir = os.path.isdir(location)
msgSend(isDir)

# zip directory
zipCheck = msgDecode()
zippedDir = socket.gethostname() + "_" + location
if zipCheck == "ZIP":
    shutil.make_archive(zippedDir, "tar", location)
    zippedDir = zippedDir + ".tar"
    msgSend("ZIPPED")

# alert server of the archive file size
zipSize = os.path.getsize(zippedDir)
msgSend(zipSize)

# transfer archive
if msgDecode() == "SEND_ARCHIVE":
    msgSend(zippedDir)
    fileDir = open(zippedDir, "rb")
    fileDir = fileDir.read()
    SERVER.sendfile(fileDir)
