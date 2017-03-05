#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from tkinter import *
<<<<<<< HEAD
from .DataFunctions import *

=======
from SocketFunctions import *
from DataFunctions import *
import Constants
>>>>>>> origin/master

global root

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

<<<<<<< HEAD
        #packet creation and send initial packet
        packdat = fileRead.read(PacketSize)
        sndpkt = makepkt(packdat,0,MakeChecksum(packdat))
        udt_send(sndpkt)

        #begin state machine by entering wait ack 0 state
        wait_ack_0()


        # loop to read and send packets to the server
        #while message != b"":
        #    packet = message
        #    clientSocket.sendto(packet, (ServerName, ServerPort))
        #    message = fileRead.read(PacketSize)

        # Send a final message to the server to signify end
        clientSocket.sendto(TerminateCharacter, (ServerName, ServerPort))
=======
        TransmitFile(fileRead)
>>>>>>> origin/master

        fileRead.close()




    ######## Function:
    ######## wait_ack_0
    #### Purpose:
    #### one of the two states in this state machine,
    #### waits for ack 0 then sends next packet and goes to next state
    ## Paramters:
    ## None
    def wait_ack_0(self):
        #if ack was received
        if rdt_rcv(rcvpkt)==1:
            #if corrupt or wrong sn resend
            if CheckChecksum(rcvpkt)==False or isAck(rcvpkt,1):
                udt_send(sndpkt)
                wait_ack_0()
            #if not corrupt and correct sn send new packet and change state
            if CheckChecksum(rcvpkt)==True and isAck(rcvpkt,0):
                packdat = fileRead.read(PacketSize)
                sndpkt = makepkt(packdat, 1, MakeChecksum(packdat))
                udt_send(sndpkt)
                wait_ack_1()
        #loop back if ack not recieved
        wait_ack_0()

    ######## Function:
    ######## wait_ack_1
    #### Purpose:
    #### one of the two states in this state machine,
    #### waits for ack 1 then sends next packet and goes to next state
    ## Paramters:
    ## None
    def wait_ack_1(self):
        #if packet was received
        if rdt_rcv(rcvpkt)==1:
            # if corrupt or wrong sn resend
            if CheckChecksum(rcvpkt)==False or isAck(rcvpkt,0):
                udt_send(sndpkt)
                wait_ack_0()
            # if not corrupt and correct sn send new packet and change state
            if CheckChecksum(rcvpkt)==True and isAck(rcvpkt,1):
                packdat = fileRead.read(PacketSize)
                sndpkt = makepkt(packdat, 0, MakeChecksum(packdat))
                udt_send(sndpkt)
                wait_ack_1()
        # loop back if ack not recieved
        wait_ack_0()



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
