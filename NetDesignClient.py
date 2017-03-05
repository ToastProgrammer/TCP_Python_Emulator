#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from tkinter import *

from .DataFunctions import *
from SocketFunctions import *
from DataFunctions import *
import Constants

global root
global fileRead

global clientSocket
clientSocket = socket(AF_INET, SOCK_DGRAM)

class App(Frame):
    # Tkinter initializing
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()


        self.instructions = Text(height=2, width=15)
        self.instructions.pack()
        self.instructions.insert(END, "Enter name of\n local file.")


        # GUI will have place for string entry entryPath
        # entryPath will be at the bottom of the GUI
        self.entryPath = Entry()
        self.entryPath.pack()
        self.contents = StringVar()

        # Default contents of variable will be null
        self.contents.set('')
        # tell the entry widget to watch this variable
        self.entryPath["textvariable"] = self.contents

        # Begin send_file member function on press of enter key
        self.entryPath.bind('<Key-Return>',
                            self.send_file)

    ######## Function:
    ######## send_file
    #### Purpose:
    #### Take input string file name from GUI. Open and send file to server
    ## Paramters:
    ## None

    def send_file(self, event):

        # Get variable obtained via GUI
        srcFile = self.contents.get()
        # Procedure to automatically close window if invalid file is given
        try:
            fileRead = open(srcFile, "rb")
        except FileNotFoundError:
            print(srcFile, "not found")
            self.Quit()
            raise
        except:
            self.Quit()
            raise

        #packet creation and send initial packet
        packdat = fileRead.read(PacketSize)
        sndpkt = PackageHeader(packdat,0)
        udt_send(sndpkt, clientSocket)
        #begin state machine by entering wait ack 0 state
        self.wait_ack_0(sndpkt)

        # loop to read and send packets to the server
        #while message != b"":
        #    packet = message
        #    clientSocket.sendto(packet, (ServerName, ServerPort))
        #    message = fileRead.read(PacketSize)

        # Send a final message to the server to signify end
        clientSocket.sendto(TerminateCharacter, (ServerName, ServerPort))
        fileRead.close()




    ######## Function:
    ######## wait_ack_0
    #### Purpose:
    #### one of the two states in this state machine,
    #### waits for ack 0 then sends next packet and goes to next state
    ## Paramters:
    ## prevpkt - previous packet for potential resending
    def wait_ack_0(self, prevpkt):
        rcvpkt = rdt_rcv(clientSocket)
        #if corrupt or wrong sn resend
        if CheckChecksum(rcvpkt)==False or isAck(rcvpkt,1)==True:
            udt_send(prevpkt, clientSocket)
            self.wait_ack_0(prevpkt)
        #if not corrupt and correct sn send new packet and change state
        if CheckChecksum(rcvpkt)==True and isAck(rcvpkt,0)==True:
            packdat = fileRead.read(PacketSize)
            sndpkt = PackageHeader(packdat, 1)
            udt_send(sndpkt, clientSocket)
            self.wait_ack_1(sndpkt)
        #loop back if ack not recieved
        self.wait_ack_0(prevpkt)

    ######## Function:
    ######## wait_ack_1
    #### Purpose:
    #### one of the two states in this state machine,
    #### waits for ack 1 then sends next packet and goes to next state
    ## Paramters:
    ## prevpkt - previous packet for potential resending
    def wait_ack_1(self, prevpkt):
        #if packet was received
        rcvpkt = rdt_rcv(clientSocket)
        # if corrupt or wrong sn resend
        if CheckChecksum(rcvpkt)==False or isAck(rcvpkt,0)==True:
            udt_send(prevpkt, clientSocket)
            self.wait_ack_0(prevpkt)
        # if not corrupt and correct sn send new packet and change state
        if CheckChecksum(rcvpkt)==True and isAck(rcvpkt,1)==True:
            packdat = fileRead.read(PacketSize)
            sndpkt = PackageHeader(packdat, 0)
            udt_send(sndpkt, clientSocket)
            self.wait_ack_1(sndpkt)
        # loop back if ack not recieved
        self.wait_ack_0(prevpkt)



    ######## Function:
    ######## Quit
    #### Purpose:
    #### Quit and close tkinter GUI window on error
    ## Paramters:
    ## None
    def Quit(self):
        root.destroy()

root = Tk()
app = App(master=root)
# Run the tkinter GUI app
app.mainloop()
