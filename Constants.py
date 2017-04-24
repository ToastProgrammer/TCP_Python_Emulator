# Size of packets to send
PacketSize = 1024
# Message to signify end of file
TerminateCharacter = b''

ACK = bytes(b'\xFA')

ServerName = 'localhost'
# Port for socket to attach to
ServerPort = 12000
ClientPort = 12001

IndexSeqNum = 2
IndexSyn    = 3
IndexFin    = 4

IndexData   = 5

#create destination file
dstFile = 'dstPic.bmp'

Alpha = 0.125
Beta = 0.25
DefaultRTT = 0.2
DefaultDev = 0.01
WindowSize = 8;

SendFSM0 = "SendFSM0a.gif"
SendFSM1 = "SendFSMwa0.gif"
SendFSM2 = "SendFSM1a.gif"
SendFSM3 = "SendFSMwa1.gif"

RecvFSM0 = "RecvFSM0.gif"
RecvFSM1 = "RecvFSM1.gif"

blowShitUp = False

if(blowShitUp):
    dataCorChance   = 20
    dataLossChance  = 20
    ackCorChance    = 20
    ackLossChance   = 20
else:
    dataCorChance   = 0
    dataLossChance  = 0
    ackCorChance    = 0
    ackLossChance   = 0
