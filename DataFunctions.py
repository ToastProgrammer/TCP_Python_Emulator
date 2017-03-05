from socket import *
from Constants import *
from binascii import *

##---------------Bitwise Manipulation-----------------##
#------------------------------------------------------#

def ChecksumAddition(curSum, nextItem):
    tempInt = int.from_bytes(curSum, 'big') + int.from_bytes(nextItem, 'big')
    if tempInt >= 65536: #overflow
        tempInt = (tempInt % 65536) + 1
    return(bytearray(tempInt.to_bytes(2, 'big')))

def MakeChecksum(bString):
    checksum = bytearray(b'\x00\x00')  ## Returns 16 bit bytes object (b'\x00\x00')
    localIndex = 0
    for x in bString:
        if localIndex is 0:
            tempBytes = bytearray(x)
            localIndex = 1
        else:
            tempBytes.append(x)
            checksum = ChecksumAddition(checksum,tempBytes)
            localIndex = 0
    print(checksum)
    return checksum

def CheckChecksum(bString):
    checkString = MakeChecksum(bString[2:])
    checkArray = bytearray(checkString)
    recievedArray = bytearray(bString[0:-2])
    if (checkArray[1] == recievedArray[1]) and (checkArray[0] == recievedArray[0]):
        return True
    else:
        return False

def InsertChecksum(data, checksum):
    return bytes(checksum + data)

def RemoveChecksum(bString):
    return bString[2:]

def AddSequenceNum(seq, seqNum):
    return bytes([seqNum]) + seq

def RemoveSequenceNum(seq):
    return seq[1:]

def CheckSequenceNum(seq, seqNum):
    InSequence = False
    if seq[1] is seqNum:
        InSequence = True
        return InSequence, RemoveSequenceNum(seq)
    else:
        return InSequence

def PackageHeader(data, seq):
    Segment = AddSequenceNum(data, seq)
    return InsertChecksum(Segment, MakeChecksum(Segment))

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

#bytearray(b'\x12\x5F\x3A')
testing = open("srcPic.png", 'rb')
t2 = testing.read(1024)
print(type(t2))
print(t2)
a = MakeChecksum(t2)
print(type(a))
t2 = a + t2
print(type(t2))
print(CheckChecksum(t2))
print(bytes(t2))