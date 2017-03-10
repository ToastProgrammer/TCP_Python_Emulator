#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose
from binascii import *
from SocketFunctions import *
from DataFunctions import *
from socket import *
from Constants import *

global writeIndex

######## Function:
######## wait_for_0
#### Purpose:
#### one of the two states in this state machine,
#### waits for packet with sn=0 then sends an ack and goes to next state
## Paramters:
## None
def wait_for_0(serverSocket, onceThrough, writeIndex):

    rcvpkt = rdt_rcv(serverSocket)
    moreData = True
    if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt,0):
        data = UnpackageHeader(rcvpkt)
        moreData = deliver_data(data, writeIndex)
        sndpkt = PackageHeader(ACK,0)
        udt_send(sndpkt, serverSocket, ClientPort)
        onceThrough = True
        seqNum = 1
    elif onceThrough:
        sndpkt = PackageHeader(ACK, 0)
        udt_send(sndpkt, serverSocket, ClientPort)
        moreData = True
        seqNum = 0
    else:
        seqNum = 0
    return onceThrough, moreData, seqNum, writeIndex


######## Function:
######## wait_for_1
#### Purpose:
#### one of the two states in this state machine,
#### waits for packet with sn=1 then sends an ack and goes to next state
## Paramters:
## None
def wait_for_1(serverSocket, onceThrough, writeIndex):

    rcvpkt = rdt_rcv(serverSocket)
    if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt,1):
        data = UnpackageHeader(rcvpkt)
        moreData = deliver_data(data, writeIndex)
        sndpkt = PackageHeader(ACK,1)
        udt_send(sndpkt, serverSocket, ClientPort)
        onceThrough = True
        seqNum = 0
    elif onceThrough:
        sndpkt = PackageHeader(ACK, 1)
        udt_send(sndpkt, serverSocket, ClientPort)
        seqNum = 1
        moreData = True
    else:
        seqNum = 1
        moreData = True
    return onceThrough, moreData, seqNum, writeIndex

######## Function:
######## deliver data
#### Purpose:
#### delivers the data from packet and appends to file
## Paramters:
## Data in
def deliver_data(data, writeIndex):
    moreData = True
    fileWrite = open(dstFile, 'ab')
    fileWrite.write(data)
    fileWrite.seek(PacketSize * writeIndex)
    #if EOF close file
    writeIndex += 1
    if data == b'':
        fileWrite.close()
        moreData = False
    return moreData, writeIndex

#setup socket
def ServerMain():

    serverSocket = socket(AF_INET, SOCK_DGRAM)

    serverSocket.bind(('',ServerPort))

    print ('The server is ready to receive')

    while 1:
        # Wait here until recieve message from socket


        seqNum = 0
        moreData = True
        onceThrough = True
        writeIndex = 0
        while(moreData):
            if seqNum is 0:
                onceThrough, moreData, seqNum, writeIndex = wait_for_0(serverSocket, onceThrough, writeIndex)
            if(moreData):
                if seqNum is 1:
                    onceThrough, moreData, seqNum, writeIndex = wait_for_1(serverSocket, onceThrough, writeIndex)

ServerMain()