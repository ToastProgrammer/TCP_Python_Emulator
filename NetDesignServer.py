#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose
from binascii import *
from SocketFunctions import *
from DataFunctions import *
from socket import *
from .DataFunctions import *
import Constants

#setup socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',ServerPort))

#define ACK
ACK = bytearray(b'\xFA')

#create destination file
dstFile = 'dstPic.png'
#oncethrough just becomes 1 if the state machine has started
oncethrough = 0

print ('The server is ready to receive')

######## Function:
######## wait_for_0
#### Purpose:
#### one of the two states in this state machine,
#### waits for packet with sn=0 then sends an ack and goes to next state
## Paramters:
## None
def wait_for_0():
    rcvpkt = rdt_rcv(serverSocket)
    if CheckChecksum(rcvpkt)==True and CheckSequenceNum(rcvpkt,0)==True:
        data = UnpackageHeader(rcvpkt)
        deliver_data(data)
        sndpkt = PackageHeader(ACK,0)
        udt_send(sndpkt, serverSocket)
        oncethrough = 1
        wait_for_1()
    if CheckChecksum(rcvpkt)==False or CheckSequenceNum(rcvpkt,1)==True:
        if oncethrough==1:
            udt_send(sndpkt, serverSocket)
    wait_for_0()

######## Function:
######## wait_for_1
#### Purpose:
#### one of the two states in this state machine,
#### waits for packet with sn=1 then sends an ack and goes to next state
## Paramters:
## None
def wait_for_1():
    rcvpkt = rdt_rcv(serverSocket)
    if CheckChecksum(rcvpkt)==True and CheckSequenceNum(rcvpkt,1)==True:
        data = UnpackageHeader(rcvpkt)
        deliver_data(data)
        sndpkt = PackageHeader(ACK, 1)
        udt_send(sndpkt, serverSocket)
        wait_for_0()
    if CheckChecksum(rcvpkt)==False or CheckSequenceNum(rcvpkt,0)==True:
        udt_send(sndpkt, serverSocket)
    wait_for_1()

######## Function:
######## deliver data
#### Purpose:
#### delivers the data from packet and appends to file
## Paramters:
## Data in
def deliver_data(data):
    fileWrite = open(dstFile, 'ab')
    fileWrite.write(data)
    fileWrite.seek(PacketSize)
    #if EOF close file
    if data == b"":
        fileWrite.close()
    return



