from socket import *
from Constants import *
import random


##-----------------Socket Functions-------------------##
#------------------------------------------------------#
#def Client_Wait(ServerName, ServerPort, seqNum, prevPacket):


def udt_send(packet, socket):
    socket.sendto(packet, (ServerName, ServerPort))

def rdt_rcv(socket):
    rcvpkt, clientAddress = socket.recvfrom(2048)
    return rcvpkt



