#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose
from binascii import *
from SocketFunctions import *
from DataFunctions import *
from socket import *
from Constants import *

global fileWrite

#create destination file
dstFile = 'dstPic.png'

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
        print('Checksum was valid')
        data = UnpackageHeader(rcvpkt)
        moreData = deliver_data(data)
        sndpkt = PackageHeader(ACK,0)
        udt_send(sndpkt, serverSocket)
        onceThrough = True
        seqNum = 1
    elif onceThrough:
        print('Checksum was invalid')
        sndpkt = PackageHeader(ACK, 1)
        udt_send(sndpkt, serverSocket)
        onceThrough = False
        seqNum = 0
    else:
        print("error")
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
    moreData = True
    if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt,0):
        data = UnpackageHeader(rcvpkt)
        moreData = deliver_data(data)
        sndpkt = PackageHeader(ACK,1)
        udt_send(sndpkt, serverSocket)
        onceThrough = True
        seqNum = 0
    elif onceThrough:
        sndpkt = PackageHeader(ACK, 0)
        udt_send(sndpkt, serverSocket)
        onceThrough = False
        seqNum = 1
    else:
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
    fileWrite.write(data)
    fileWrite.seek(2048)
    #if EOF close file
    if data == b"":
        fileWrite.close()
        moreData = False
    return moreData

#setup socket
def ServerMain():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    try:
        serverSocket.bind(('',ServerPort))
    except OSError:
        serverSocket.close()
        serverSocket.bind(('', ServerPort))

    print ('The server is ready to receive')

    fileWrite = open(dstFile, 'ab')

    #oncethrough just becomes 1 if the state machine has started



    while 1:
        # Wait here until recieve message from socket

        # Write local file
        fileWrite = open(dstFile, 'ab')

        seqNum = 0
        moreData = True
        onceThrough = True

        while(moreData):
            if seqNum is 0:
                onceThrough, moreData, seqNum = wait_for_0(serverSocket, onceThrough)
            if seqNum is 1:
                print('1')
                onceThrough, moreData, seqNum= wait_for_1(serverSocket, onceThrough)
        print("Finished")


ServerMain()
print("Should not be here")