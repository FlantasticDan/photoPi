#!/usr/bin/env python3

# Connects to and controls other pis on the LAN

import time
import socket
import sys
import shutil
import statistics
import spur

print("### CAPTURE SERVER STARTING ###")

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
while count < 2:
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
pathClient = CLIENT[0] + PATH[0] + "captureClient.py"
while count < CLIENTS:
    clientSSH.append(openSSH(CLIENT[count], sshKey[0], sshKey[1]))
    with clientSSH[count]:
        clientSSH[count].run(["wget", "-N", pathClient])
        clientSSH[count].spawn(["python", "captureClient.py", str(CLIENT[0]), str(port[count])])
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
fileName = input("File Name: ")
imgFormat = input("Image Format [jpeg/png/bmp/yuv/rgb/bgr]: ")
while True: # input verification
    if imgFormat in ["jpeg", "png", "bmp", "yuv", "rgb", "bgr"]:
        break
    else:
        imgFormat = input("[!] Invalid Format, Try Again [jpeg/png/bmp/yuv/rgb/bgr]: ")
originalCount = input("Sequence Lenth [#]: ")
while True: # int input verification
    try:
        originalCount = int(originalCount)
        break
    except ValueError:
        originalCount = input("[!] Invalid Number, Try Again [#]: ")

# send user inputs to clients
sendMsgAllClients(fileName)
sendMsgAllClients(imgFormat)

# exposure calibration via host camera
clientSocket[0].sendall(msgEncode("EXPOSURE"))
sys.stdout.write("Generating Exposure Profiles...")
sys.stdout.flush()
clientMsg[0] = msgDecode(clientSocket[0])
if clientMsg[0] == "GENERATED":
    sys.stdout.write("\rExposure Profiles Generated:   \n")
    sys.stdout.flush()
    pathExposure = PATH[1] + fileName + "_Profiles"
    shutil.copytree("/home/{}/{}_Profiles".format(sshKey[0], fileName), pathExposure)
    count = 1
    while count <= 5:
        print("{} - http://{}{}{}_Profiles/{}.jpeg".format(count, CLIENT[0], 
            PATH[0], fileName, count))
        count += 1
exposureProfile = input("Select an Exposure Profile: ")
while True: # int input verification
    try:
        exposureProfile = int(exposureProfile)
        if exposureProfile <=5 and exposureProfile > 0:
            break
        else:
            exposureProfile = input("[!] Invalid Profile, Try Again [#]: ")
    except ValueError:
        exposureProfile = input("[!] Invalid Profile, Try Again [#]: ")
sendMsgAllClients(exposureProfile)
recieveMsgAllClients()
if all(i == "EXPOSED" for i in clientMsg) is False:
    raise RuntimeError("Unable to Calibrate Exposure on Client(s)")
else:
    print("Exposure Calibrated on All Clients")

# alert user of impending capture sequence
sys.stdout.write("Starting Capture in 5")
sys.stdout.flush()
delay = 5
time.sleep(1)
while delay > 0:
    delay -= 1
    sys.stdout.write("\rStarting Capture in {}".format(delay))
    time.sleep(1)
    sys.stdout.flush()

statusHeader = "(  CYCLES  )  [{:^25}]  (  ETA  )".format("PROGRESS")
sys.stdout.write("\r{}\n".format(statusHeader))

TIMING = []

def statusUpdate(cycle):
    progress = round((cycle / originalCount) * 25)
    progressPrint = "#" * progress
    progressGap = " " * (25 - len(progressPrint))
    eta = round(statistics.mean(TIMING) * (originalCount - cycle))
    etaPrint = time.strftime("%M:%S", time.gmtime(eta))
    sys.stdout.write("\r({:>3} of {:<3})  [{}{}]  ({:^7})".format(cycle, 
        originalCount, progressPrint, progressGap, etaPrint))
    sys.stdout.flush()


cycle = 1
while cycle <= originalCount:
    start = time.time()
    sendMsgAllClients("CAPTURE")
    recieveMsgAllClients()
    if all(i == "CAPTURED" for i in clientMsg) is True:
        elapsed = time.time() - start
        TIMING.append(elapsed)
        statusUpdate(cycle)
        cycle += 1

# close sockets on clients and on host
sendMsgAllClients("DONE")
count = 0
while count < CLIENTS:
    clientSocket[count].close
    count += 1
print("")
print("### CAPTURE COMPLETED SUCCESSFULLY ###")
