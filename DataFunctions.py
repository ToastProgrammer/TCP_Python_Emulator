from socket import *
from Constants import *
from random import *

# Random bit errors
corruptDictionary = {0 : b'\x01', 1 : b'\x02', 2 : b'\x04', 3 : b'\x08',
                     4 : b'\x10', 5 : b'\x20', 6 : b'\x40', 7 : b'\x80'}

##---------------Bitwise Manipulation-----------------##
#------------------------------------------------------#

##---------------Checksum-----------------##
#Function for adding segments to checksum
def ChecksumAddition(curSum, nextItem):
    tempInt = int.from_bytes(curSum, 'big') + int.from_bytes(nextItem, 'big')
    if tempInt >= 65536: #overflow
        tempInt = (tempInt % 65536) + 1
    return(bytearray(tempInt.to_bytes(2, 'big')))

# Make checksum for 16-bit segments
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
    intChecksum = int.from_bytes(checksum, 'big') ^ 0xFF    ##1's compliment
    return intChecksum.to_bytes(2,'big')

# Check if sequence number + data matches checksum
def CheckChecksum(bString):
    checkString = MakeChecksum(bString[IndexSeqNum:])
    checkArray = bytearray(checkString)
    recievedArray = bytearray(bString)
    if (checkArray[1] == recievedArray[1]) and (checkArray[0] == recievedArray[0]):
        return True
    else:
        return False

# Insert checksum on seq# + data
def InsertChecksum(data, checksum):
    return bytes(checksum + data)

# Remove checksum from seq# + data
def RemoveChecksum(bString):
    return bString[IndexSeqNum:]


##---------------Sequence Number-----------------##
# Insert seq# to data
def AddSequenceNum(seq, seqNum):
    return bytes([seqNum]) + seq

# Remove seq# from data
def RemoveSequenceNum(seq):
    return seq[IndexSeqNum+1:]

def GetSequenceNum(seq):
    return seq[IndexSeqNum]

# Check sequence number from recieved packet
def CheckSequenceNum(seq, seqNum):
    if GetSequenceNum(seq) == seqNum:
        return True
    return False

def CheckHigherSeq(seq, seqNum):
    if GetSequenceNum(seq) >= seqNum:
        return True
    return False

# Check if looped sequence number is within window size to be acked
def CheckWithinLoop(windowSize, curBase, recAck):
    print()
    if ((MaxSequenceNum - curBase) + recAck <= windowSize):
        return True
    else:
        return False

def GetNumPacketsBetween(oldBase, base, maxSeqNum):
    if base >= oldBase:
        retVal = base - oldBase
    else:
        retVal = (maxSeqNum - oldBase) + base + 1
    print("Packets between", oldBase, "and", base, "is", retVal)
    return retVal

##-----------------Syn/Fin Flags------------------##
def SetSynFin(data, syn, fin):
    if fin:
        data = bytes([1]) + data
    else:
        data = bytes([0]) + data
    if syn:
        data = bytes([1]) + data
    else:
        data = bytes([0]) + data
    return data

def CheckSyn(data):
    if (data[IndexSyn] == 1):
        return True
    else:
        return False

def CheckFin(data):
    if (data[IndexFin] == 1):
        return True
    else:
        return False


##---------------Packet Functions-----------------##
# Add checksum, seq#, and possible corruption
def PackageHeader(data, seq, syn = False, fin = False):
    data = SetSynFin(data, syn, fin)
    Segment = AddSequenceNum(data, seq)
    packet = InsertChecksum(Segment, MakeChecksum(Segment))
    return packet

# Return data from packet
def UnpackageHeader(segment):
    return (segment[IndexData:])

# Check last byte of packet if it is ACK
def IsAck(segment, seqNum):
    if (UnpackageHeader(segment) == ACK):
        if CheckSequenceNum(segment,seqNum):
            return True
    return False

# Determine if to corrupt packet or not
def CorruptCheck(pkt, corChance):
    seed()
    if (randint(0, 100) < corChance):
        pkt = CorruptPacket(pkt)
    return pkt

# Add random bit error to packet.
def CorruptPacket(bString):
    bString += (corruptDictionary[randint(0,7)]) + (corruptDictionary[randint(0,7)])
    return bString

def LossCheck(lossChance):
    seed()
    if (randint(0, 100) < lossChance):
        return True     # If a hit, then the packet was lost
    else:
        return False    # Otherwise the packet is sent