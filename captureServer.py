#!/usr/bin/env python3

# Connects to and controls other pis on the LAN

import time
import datetime
import os
import socket
import spur

# identify client IPs
clientFile = open("clientIP.txt", "r")
client = clientFile.readlines()
clientFile.close()
for ip in client:
    client[ip] = client[ip] - "/n"
clients = len(client)

# identify ssh credentials
sshFile = open("ssh.txt", "r")
sshKey = sshFile.readlines()
sshFile.close()
for key in sshKey:
    sshKey[key] = sshKey[key] - "/n"

# identify dependencies path
pathFile = open("path.txt", "r")
path = pathFile.readline()
pathFile.close()

# create client ports
count = 0
port = []
while (count <= clients):
    port.append(2000 + count)

# open a socket on server @ localhost:port
def openSocket(x):
    hostServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostServer.bind(client[0], x)
    hostServer.listen(1)
    clientPort, clientIP = hostServer.accept()
    return clientPort

# open the sockets
count = 1
clientSocket = [""]
while (count <= clients):
    clientSocket.append(openSocket(port[count]))

# open a SSH connection
def openSSH(host):
    sshClient = spur.SshShell(host, sshKey[0], sshKey[1])
    return sshClient

# open the SSH connections & download script
count = 1
clientSSH = [""]
path = client[0] + path + "captureClient.py"
while (count <= clients):
    clientSSH.append(openSSH(client[count]))
    with clientSSH[count]:
        clientSSH[count].run(["wget", path])
        clientSSH[count].run(["captureClient.py"])
