#!/usr/bin/env python3

# Connects to and controls other pis on the LAN

import time
import datetime
import os
import socket
import sys
import spur

# identify client IPs
clientFile = open("clientIP.txt", "r")
client = clientFile.readlines()
clientFile.close()
clients = len(client)
count = 0
while count < clients:
    client[count] = client[count].rstrip()
    count += 1

# identify ssh credentials
sshFile = open("ssh.txt", "r")
sshKey = sshFile.readlines()
sshFile.close()
count = 0
while count < 2:
    sshKey[count] = sshKey[count].rstrip()
    count += 1

# identify dependencies path
pathFile = open("path.txt", "r")
path = pathFile.readline()
pathFile.close()
path = path.rstrip()

# create client ports
count = 0
port = []
while count < clients:
    port.append(2000 + count)
    count += 1

# open a socket on server @ localhost:port
def openSocket(client, port):
    hostServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostServer.bind((client, port))
    hostServer.listen(0)
    return hostServer

# open the sockets and create the client array
count = 0
clientServer = []
clientSocket = []
clientMsg = []
while count < clients:
    clientServer.append(openSocket(client[0], port[count]))
    clientSocket.append("")
    clientMsg.append("")
    count += 1

# open a SSH connection
def openSSH(host, user, pwd):
    sshClient = spur.SshShell(host, user, pwd)
    return sshClient

# open the SSH connections, download script to clients, and pass calibration
count = 0
clientSSH = []
path = client[0] + path + "captureClient.py"
while count < clients:
    clientSSH.append(openSSH(client[count], sshKey[0], sshKey[1]))
    with clientSSH[count]:
        clientSSH[count].run(["wget", "-N", path])
        clientSSH[count].run(["python", "captureClient.py", str(client[0]), str(port[count])])
    count += 1

# utf-8 byte reciever, buffer, and decoder
def msgDecode(client):
    chunck = client.recv(16)
    chunck = chunck.decode()
    msgLength = int(chunck[:4])
    msg = chunck[4:]
    while len(msg) < msgLength:
        chunck = client.recv(16)
        chunck = chunck.decode()
        msg += chunck
    return msg

# accept connection on socket
def connectSocket(cServer):
    clientSocket, ip = cServer.accept()
    return clientSocket

# accept the connections on the sockets
count = 0
while count < clients:
    sys.stdout.write("(" + "{:>2}".format(count + 1) + " / {}) Connecting".format(clients))
    sys.stdout.flush()
    clientSocket[count] = connectSocket(clientServer[count])
    clientMsg[count] = msgDecode(clientSocket[count])
    sys.stdout.write("\r(" + "{:>2}".format(count + 1) + " / {})".format(clients))
    print(" Connected to {} ({})".format(clientMsg[count], client[count]))
    sys.stdout.flush()
    count += 1

# utf-8 byte encoder with injected header
def msgEncode(message):
    msg = str(message)
    msgLength = len(msg)
    msg = "{:<4}".format(msgLength) + msg
    msg = msg.encode()
    return msg
