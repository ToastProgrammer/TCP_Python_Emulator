#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from socket import *

srcFile = 'srcPic.png'


serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)


fileRead =  open(srcFile, "rb")

packet = fileRead.read(2048)
while packet != b"":
    message = packet
    clientSocket.sendto(message,(serverName, serverPort))
    packet = fileRead.read(2048)


fileRead.close()
clientSocket.close()