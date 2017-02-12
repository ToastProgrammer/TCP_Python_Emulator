#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))

dstFile = 'dstPic.png'
fileWrite = open(dstFile, 'ab')


print ('The server is ready to receive')
while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    fileWrite.write(message)
    fileWrite.seek(2048)
    if message == b"":
        fileWrite.close()

