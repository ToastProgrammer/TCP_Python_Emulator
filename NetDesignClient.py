#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from socket import *

srcFile = 'testRead.txt'
dstFile = 'testWrite.txt'

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

fileWrite = open(dstFile, 'wb')
fileRead =  open(srcFile, "rb")

packet = fileRead.read(2048)
while packet != b"":
    message = packet
    clientSocket.sendto(message,(serverName, serverPort))
    message, serverAddress = clientSocket.recvfrom(2048)
    fileWrite.write(message)
    packet = fileRead.read(2048)

fileWrite.close()
fileRead.close()
clientSocket.close()

#Testing Github
