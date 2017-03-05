from socket import *
from Constants import *

##-----------------Socket Functions-------------------##
#------------------------------------------------------#
def TransmitFile(fileRead):
    # Setup socket
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # initial read of file
    message = fileRead.read(PacketSize)
    # loop to read and send packets to the server
    while message != b"":
        packet = message
        clientSocket.sendto(packet, (ServerName, ServerPort))
        message = fileRead.read(PacketSize)

    # Send a final message to the server to signify end
    clientSocket.sendto(TerminateCharacter, (ServerName, ServerPort))

    # End by closing the file and the socket
    clientSocket.close()