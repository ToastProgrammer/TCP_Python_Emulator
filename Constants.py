# Size of packets to send
PacketSize = 2
# Message to signify end of file
TerminateCharacter = b''

ACK = bytes(b'\xFA')

ServerName = 'localhost'
# Port for socket to attach to
ServerPort = 12000
ClientPort = 12001


#create destination file
dstFile = 't.txt'

