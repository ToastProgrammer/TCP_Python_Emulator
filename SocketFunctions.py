from socket import *
from Constants import *
import random


##-----------------Socket Functions-------------------##
#------------------------------------------------------#
def udt_send(packet, socket):
    socket.sendto(packet, (ServerName, ServerPort))

def rdt_rcv(socket):
    rcvpkt, clientAddress = socket.recvfrom(PacketSize)
    return rcvpkt



