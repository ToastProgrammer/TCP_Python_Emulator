#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose
from binascii import *
from SocketFunctions import *
from DataFunctions import *
from socket import *
from threading import *
from Constants import *
from time import clock, sleep
from os import remove

writeIndex = 0
moreData = True
fileWrite = None
newFile = True
serverSocket = None
waitForAck = True


def checkTeardownAck(expectedSeqNum):
    global serverSocket
    global waitForAck

    while waitForAck:
        rcvpkt = rdt_rcv(serverSocket)
        if(CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt, expectedSeqNum) and CheckFin(rcvpkt)):
            waitForAck = False



#---------------------------- D e l i v e r   D a t a --------------------------
def deliver_data(data):
    global writeIndex
    global moreData
    global fileWrite
    global newFile

    if newFile:
        fileWrite = open(dstFile, 'wb')
        newFile = False
    else:
        fileWrite = open(dstFile, 'ab')
    #fileWrite.seek(0)
    #fileWrite.seek(PacketSize * writeIndex, 0)
    fileWrite.write(data)
    #if EOF close file
    writeIndex += PacketSize

#---------------------------- S e r v e r   M a i n ----------------------------
def ServerMain():

    global writeIndex
    global moreData
    global newFile
    global waitForAck
    global serverSocket

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('',ServerPort))

    connectionBreakdown = False

    print ('The server is ready to receive')

    while 1:

        moreData            = True
        newFile             = True

        connectionSetup     = True
        connectionBreakdown = False

        expectedSeqNum = 1



        synPkt = PackageHeader(ACK, 0, syn=True)
        sndpkt = PackageHeader(ACK,expectedSeqNum)  # Pack first ACK
        while(moreData):
            rcvpkt = rdt_rcv(serverSocket)


            # CONNECTION SETUP **************************************
            while(connectionSetup):
                if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt, 0) and CheckSyn(rcvpkt):
                    udt_send(synPkt, serverSocket, ClientPort)
                rcvpkt = rdt_rcv(serverSocket)
                if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt, expectedSeqNum) and CheckSyn(rcvpkt) == False:
                    connectionSetup = False

            if CheckChecksum(rcvpkt) and CheckSequenceNum(rcvpkt, expectedSeqNum):  # If Checksum & seq num correct
                expectedSeqNum += 1
                if expectedSeqNum > MaxSequenceNum:
                    expectedSeqNum = 1  # loop after 255, only one byte for seqNum
                data = UnpackageHeader(rcvpkt)
                deliver_data(data)  # Write correct data to file
                if (CheckFin(rcvpkt)):  # If FIN flag is set, begin connection teardown
                    connectionBreakdown = True
                    moreData = False
                sndpkt = PackageHeader(ACK, expectedSeqNum, fin=connectionBreakdown)  # Package ack, seq (and fin?)
                udt_send(sndpkt, serverSocket, ClientPort)
                #onceThrough = True
            else:
                udt_send(sndpkt, serverSocket, ClientPort)

        # ENTERING CONNECTION BREAKDOWN
        waitForAck = True
        sndpkt = PackageHeader(ACK, expectedSeqNum, fin=True)

        checkThread = Thread(None, checkTeardownAck, "Check for C Fin ACK", args=[expectedSeqNum])
        checkThread.start()
        while (waitForAck):
            udt_send(sndpkt, serverSocket, ClientPort)
            sleep(.1)
        waitForAck = True

        print("=================SUCCESS======================")

        print("Waiting for new connection")




ServerMain()