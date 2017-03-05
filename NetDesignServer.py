#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose
from binascii import *
from SocketFunctions import *
from DataFunctions import *
from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))

dstFile = 'dstPic.png'

print ('The server is ready to receive')
while 1:
    # Wait here until recieve message from socket
    message, clientAddress = serverSocket.recvfrom(2048)
    # Write local file
    fileWrite = open(dstFile, 'ab')
    fileWrite.write(message)
    fileWrite.seek(2048)
    # If EOF, close the file
    if message == b"":
        fileWrite.close()

