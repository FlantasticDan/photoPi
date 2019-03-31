#!/usr/bin/env python3

# controls individual pis locally based on LAN commands

import socket
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((sys.argv[1], int(sys.argv[2])))
