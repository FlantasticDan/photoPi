#!/usr/bin/env python3

# controls individual pis locally based on LAN commands

import socket
import sys

# utf-8 byte encoder with injected header
def msgEncode(message):
    msg = str(message)
    msgLength = len(msg)
    msg = "{:<4}".format(msgLength) + msg
    msg = msg.encode()
    return msg

# server connection and client identification
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((sys.argv[1], int(sys.argv[2])))
server.send(msgEncode(socket.gethostname()))
