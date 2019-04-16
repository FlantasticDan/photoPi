#!/usr/bin/env python3

# Connects to and retrieves photos from remote Pis

import time
import socket
import sys
import shutil
import statistics
import spur

print("### TRANSFER SERVER STARTING ###")

# identify client IPs
clientFile = open("clientIP.txt", "r")
CLIENT = clientFile.readlines()
clientFile.close()
CLIENTS = len(CLIENT) # global constant, number of clients
count = 0
while count < CLIENTS:
    CLIENT[count] = CLIENT[count].rstrip()
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
PATH = pathFile.readlines()
pathFile.close()
count = 0
while count < 3:
    PATH[count] = PATH[count].rstrip()
    count += 1

# create client ports
count = 0
port = []
while count < CLIENTS:
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
while count < CLIENTS:
    clientServer.append(openSocket(CLIENT[0], port[count]))
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
pathClient = CLIENT[0] + PATH[0] + "transferClient.py"
while count < CLIENTS:
    clientSSH.append(openSSH(CLIENT[count], sshKey[0], sshKey[1]))
    with clientSSH[count]:
        clientSSH[count].run(["wget", "-N", pathClient])
        clientSSH[count].spawn(["python3", "transferClient.py", str(CLIENT[0]), str(port[count])])
    count += 1
    
# utf-8 byte reciever, buffer, and decoder
def msgDecode(client):
    chunk = client.recv(1)
    while len(chunk) < 4:
        chunk += client.recv(1)
    chunk = chunk.decode()
    msgLength = int(chunk[:4])
    msg = chunk[4:]
    while len(msg) < msgLength:
        chunk = client.recv(1)
        chunk = chunk.decode()
        msg += chunk
    return msg

# accept connection on socket
def connectSocket(cServer):
    clientSocket, ip = cServer.accept()
    return clientSocket

# accept the connections on the sockets
count = 0
while count < CLIENTS:
    sys.stdout.write("(" + "{:>2}".format(count + 1) + " / {}) Connecting".format(CLIENTS))
    sys.stdout.flush()
    clientSocket[count] = connectSocket(clientServer[count])
    clientMsg[count] = msgDecode(clientSocket[count])
    sys.stdout.write("\r(" + "{:>2}".format(count + 1) + " / {})".format(CLIENTS))
    print(" Connected to {} ({})".format(clientMsg[count], CLIENT[count]))
    sys.stdout.flush()
    count += 1

# utf-8 byte encoder with injected header
def msgEncode(message):
    msg = str(message)
    msgLength = len(msg)
    msg = "{:<4}".format(msgLength) + msg
    msg = msg.encode()
    return msg

# send message to all clients
def sendMsgAllClients(message):
    msg = msgEncode(message)
    count = 0
    while count < CLIENTS:
        clientSocket[count].send(msg)
        count += 1

def recieveMsgAllClients():
    count = 0
    while count < CLIENTS:
        clientMsg[count] = msgDecode(clientSocket[count])
        count += 1

# query user
location = input("File Name: ")
delete = input("Delete from Source? [Y/n]: ")
if delete == "Y":
    DELETE = True
else:
    DELETE = False

# confirm directory exists on clients
sendMsgAllClients(location)
recieveMsgAllClients()
if all(i == "True" for i in clientMsg) is False:
    raise RuntimeError("Directory {} does not exist on Client(s)".format(location))
else:
    print("Directory Found on All Clients\n")

# zip client directories
sendMsgAllClients("ZIP")
print("Compressing photos on clients...")
start = time.time()
recieveMsgAllClients()
if all(i == "ZIPPED" for i in clientMsg) is True:
    finish = time.time()
    totalTime = finish - start
    printTime = time.strftime("%M:%S", time.gmtime(totalTime))
    print("Compression Completed in {}".format(printTime))

# determine disk space requirements
recieveMsgAllClients()
TOTALSIZE = 0
for msg in clientMsg:
    size = int(msg)
    TOTALSIZE += size
print("{:.2f} MB will be transferred to {}".format(TOTALSIZE * 0.000001, PATH[2]))
print("")

# transfer status printout
def statusUpdate(currentSize, cycle):
    progress = round((currentSize / TOTALSIZE) * 25)
    progressPrint = "#" * progress
    progressGap = " " * (25 - len(progressPrint))
    dataPrint = currentSize * 0.000001
    totalPrint = TOTALSIZE * 0.000001
    data = "{:.2f} of {:.2f} MB".format(dataPrint, totalPrint)
    sys.stdout.write("\r({:^19})  [{}{}]  ({:>3} of {:>3}".format(data, progressPrint, progressGap, cycle, CLIENTS))
    sys.stdout.flush()


# get archives from clients
count = 0
command = msgEncode("SEND_ARCHIVE")
statusHeader = "({:^19})  [{:^25}]  ({:^10})".format("DATA", "PROGRESS", "ARCHIVE")
sys.stdout.write("\r{}\n".format(statusHeader))
sys.stdout.flush()
while count < CLIENTS:
    clientSocket[count].send(command)
    clientSize = int(clientMsg[count])
    archive = msgDecode(clientSocket[count])
    destination = PATH[2] + archive
    zipped = open(destination, "wb")
    chunck = clientSocket[count].recv(1024)
    while len(chunck) < clientSize:
        chunck += clientSocket[count].recv(1024)
        statusUpdate(len(chunck), count + 1)
    zipped.write(chunck)
    zipped.close()
    count += 1
