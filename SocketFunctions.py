from socket import *
from Constants import *
from time import sleep
import random


##-----------------Socket Functions-------------------##
#------------------------------------------------------#
#def Client_Wait(ServerName, ServerPort, seqNum, prevPacket):


def udt_send(packet, socket, port):
    socket.sendto(packet, (ServerName, port))

def rdt_rcv(socket):
    rcvpkt, clientAddress = socket.recvfrom(2048)
    return rcvpkt



