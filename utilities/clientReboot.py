#!/usr/bin/env python3

# Connects to client machines and reboots them, does not recover connection

import time
import sys
import spur

print("#### REBOOT INITIATED ####")
print("")

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

# open a SSH connection
def openSSH(host, user, pwd):
    sshClient = spur.SshShell(host, user, pwd)
    return sshClient

# open the SSH connections and reboot clients
count = 1
clientSSH = [openSSH(CLIENT[0], sshKey[0], sshKey[1])]
while count < CLIENTS:
    clientSSH.append(openSSH(CLIENT[count], sshKey[0], sshKey[1]))
    with clientSSH[count]:
        clientSSH[count].spawn(["sudo", "reboot"])
    sys.stdout.write("\r({:>2}/{}) Clients Rebooted".format(count, CLIENTS - 1))
    sys.stdout.flush()
    count += 1

# warn user about rebooting  host
sys.stdout.write("\nRebooting THIS host in 5")
sys.stdout.flush()
delay = 5
time.sleep(1)
while delay > 0:
    delay -= 1
    sys.stdout.write("\rRebooting THIS host in {}".format(delay))
    time.sleep(1)

# reboot host
sys.stdout.write("\nREBOOTING")
clientSSH.append(openSSH(CLIENT[0], sshKey[0], sshKey[1]))
with clientSSH[0]:
    clientSSH[0].spawn(["sudo", "reboot"])
