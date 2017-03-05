#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose
from binascii import *
from SocketFunctions import *
from DataFunctions import *
from socket import *
from .DataFunctions import *

#setup socket
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('',serverPort))

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
    if rdt_rcv(rcvpkt)==1:
            if CheckChecksum(rcvpkt)==True and SeqNum(rcvpkt)==0:
                extract(rcvpkt,data)
                deliver_data(data)
                sndpkt = makepkt(ACK,0,checksum)
                udt_send(sendpkt)
                oncethrough = 1
                wait_for_1()
            if CheckChecksum(rcvpkt)==False or SeqNum(rcvpkt)==1:
                if oncethrough==1:
                    udt_send(sndpkt)
    wait_for_0()

######## Function:
######## wait_for_1
#### Purpose:
#### one of the two states in this state machine,
#### waits for packet with sn=1 then sends an ack and goes to next state
## Paramters:
## None
def wait_for_1():
    if rdt_rcv(rcvpkt)==1:
        if CheckChecksum(rcvpkt)==True and SeqNum(rcvpkt)==1:
            extract(rcvpkt, data)
            deliver_data(data)
            sndpkt = makepkt(ACK, 1, checksum)
            udt_send(sendpkt)
            wait_for_0()
        if CheckChecksum(rcvpkt)==False or SeqNum(rcvpkt)==0:
            udt_send(sndpkt)
    wait_for_1()




#while 1:
    # Wait here until recieve message from socket
    #message, clientAddress = serverSocket.recvfrom(2048)
    # Write local file
    #fileWrite = open(dstFile, 'ab')
    #fileWrite.write(message)
    #fileWrite.seek(2048)
    ## If EOF, close the file
    #if message == b"":
    #    fileWrite.close()

