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
def wait_for_0(serverSocket, onceThrough):

    rcvpkt = rdt_rcv(serverSocket)
    moreData = True
    if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt,0):
        print('recieved')
        data = UnpackageHeader(rcvpkt)
        moreData = deliver_data(data)
        sndpkt = PackageHeader(ACK,0)
        udt_send(sndpkt, serverSocket, ClientPort)
        onceThrough = True
        seqNum = 1
    elif onceThrough:
        print('oncethrough')
        sndpkt = PackageHeader(ACK, 1)
        udt_send(sndpkt, serverSocket, ClientPort)
        onceThrough = False
        seqNum = 0
    else:
        print('error')
        seqNum = 0
    return onceThrough, moreData, seqNum


######## Function:
######## wait_for_1
#### Purpose:
#### one of the two states in this state machine,
#### waits for packet with sn=1 then sends an ack and goes to next state
## Paramters:
## None
def wait_for_1(serverSocket, onceThrough):

    rcvpkt = rdt_rcv(serverSocket)
    print('rcvpkt', rcvpkt)
    moreData = True
    if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt,1):
        print('recieved')
        data = UnpackageHeader(rcvpkt)
        moreData = deliver_data(data)
        sndpkt = PackageHeader(ACK,1)
        udt_send(sndpkt, serverSocket, ClientPort)
        onceThrough = True
        seqNum = 0
    elif onceThrough:
        print('oncethrough')
        sndpkt = PackageHeader(ACK, 0)
        udt_send(sndpkt, serverSocket, ClientPort)
        onceThrough = False
        seqNum = 1
    else:
        print('error')
        seqNum = 1
    return onceThrough, moreData, seqNum

######## Function:
######## deliver data
#### Purpose:
#### delivers the data from packet and appends to file
## Paramters:
## Data in
def deliver_data(data):
    moreData = True
    fileWrite = open(dstFile, 'ab')
    fileWrite.write(data)
    fileWrite.seek(PacketSize)
    #if EOF close file
    #writeIndex += 1
    if data == b"":
        fileWrite.close()
        moreData = False
    return moreData

#setup socket
def ServerMain():

    serverSocket = socket(AF_INET, SOCK_DGRAM)

    serverSocket.bind(('',ServerPort))

    print ('The server is ready to receive')

    while 1:
        # Wait here until recieve message from socket

        # Write local file
        fileWrite = open(dstFile, 'ab')

        seqNum = 0
        moreData = True
        onceThrough = True
        writeIndex = 0
        while(moreData):
            if seqNum is 0:
                print('0')
                onceThrough, moreData, seqNum = wait_for_0(serverSocket, onceThrough)
            if seqNum is 1:
                print('1')
                onceThrough, moreData, seqNum = wait_for_1(serverSocket, onceThrough)
        break


ServerMain()