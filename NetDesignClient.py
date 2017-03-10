#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from tkinter import *
from tkinter import ttk

from DataFunctions import *
from SocketFunctions import *
from DataFunctions import *
import Constants
from time import time, sleep

global root
global fileRead
global seqNum

FILE_ENDG   = 2
FILE_CURR   = 1
FILE_STRT   = 0

class App(Frame):
    # Tkinter initializing
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("File Transfer Tool")
        self.grid(sticky=E+W+N+S)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        #-------------------------------------------
        self.instructions = Label(root, text = 'Enter file:')
        self.instructions.grid(row = 1, column = 0, padx = 3, pady = 2, sticky=W)
        #----------------
        #Variable entry for file name
        self.entryPath = Entry()
        self.entryPath.grid(row = 2, column = 0, padx = 3, pady = 2, sticky=E+W+S, columnspan =1)
        self.contents = StringVar()
        # Default contents of variable will be null
        self.contents.set('')
        # tell the entry widget to watch this variable
        self.entryPath["textvariable"] = self.contents
        # Begin send_file member function on press of enter key
        self.entryPath.bind('<Key-Return>', self.send_file)

        # -------------------------------------------

        self.timeLabel = Label(root, text='Time taken:')
        self.timeLabel.grid(row=0, column=1, padx=3, pady=2, sticky=E+S)

        # ----------------
        self.delayTime = StringVar()
        self.delay = Label(root, textvariable = self.delayTime)
        self.delay.grid(row=0, column = 2, padx = 3, pady = 2, sticky=W+N+S)
        self.delayTime.set('')

        #-------------------------------------------

        self.dataCorStr = Label(root, text='Data Error %:')
        self.dataCorStr.grid(row=1, column=1, padx=3, pady=2, sticky=E+S)
        # ----------------
        # Variable entry for % data corruption
        self.dataCorPercent = Entry()
        self.dataCorPercent.grid(row=1, column=2, padx=3, pady=2, sticky=E+S, columnspan=1)
        self.dataCor = StringVar()
        # Default contents of variable will be 0
        self.dataCor.set('0')
        # tell the entry widget to watch this variable
        self.dataCorPercent["textvariable"] = self.dataCor

        # -------------------------------------------

        self.ackCorStr = Label(root, text='ACK Error %:')
        self.ackCorStr.grid(row=2, column=1, padx=3, pady=2, sticky=E+S)
        # ----------------
        # Variable entry for % data corruption
        self.ackCorPercent = Entry()
        self.ackCorPercent.grid(row=2, column=2, padx=3, pady=2, sticky=E+S, columnspan=1)
        self.ackCor = StringVar()
        # Default contents of variable will be 0
        self.ackCor.set('0')
        # tell the entry widget to watch this variable
        self.ackCorPercent["textvariable"] = self.ackCor

        # -------------------------------------------

        self.instructions = Label(root, text='Enter file:')
        self.instructions.grid(row=1, column=0, padx=3, pady=2, sticky=W)
        # ----------------
        # Variable entry for file name
        self.entryPath = Entry()
        self.entryPath.grid(row=2, column=0, padx=3, pady=2, sticky=E + W + S, columnspan=1)
        self.contents = StringVar()
        # Default contents of variable will be null
        self.contents.set('')
        # tell the entry widget to watch this variable
        self.entryPath["textvariable"] = self.contents
        # Begin send_file member function on press of enter key
        self.entryPath.bind('<Key-Return>', self.send_file)

        # -------------------------------------------

        self.percentBytes   = IntVar(self)
        self.maxBytes       = IntVar(self)

        self.pBar = ttk.Progressbar(self, orient = "horizontal",
                                    length = 120, mode = "determinate",
                                    value=0, maximum=100)
        self.pBar.grid(row=0, column=2, padx = 3, pady = 2, sticky=E+W+N, columnspan=3)


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

        self.maxBytes = fileRead.seek(0,FILE_ENDG)    # Get total # of bytes in file and set as roof for progress bar
        self.Init_PBar()
        fileRead.seek(0, FILE_STRT)                     # Reset file position

        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.bind(('', ClientPort))

        seqNum = 0
        #packet creation and send initial packet
        packdat = fileRead.read(PacketSize)
        #start timer
        delayValue = time()

        while((packdat != b'')):

            sndpkt = PackageHeader(packdat,seqNum, int(self.dataCor.get()))
            udt_send(sndpkt, clientSocket, ServerPort)
            #begin state machine by entering wait ack 0 state
            if seqNum is 0:
                self.wait_ack_0(sndpkt, clientSocket)
            elif seqNum is 1:
                self.wait_ack_1(sndpkt, clientSocket)
            # seqNum increments, but can only be 0 or 1
            seqNum = (seqNum + 1) % 2
            packdat = fileRead.read(PacketSize)
            self.percentBytes = 100*(fileRead.seek(0, FILE_CURR)/self.maxBytes) - 1 # Update current place in file on progress bar
            self.Update_PBar()
        # Send a final message to the server to signify end
        sndpkt = PackageHeader(packdat, seqNum)
        udt_send(sndpkt, clientSocket, ServerPort)

        delayValue = time() - delayValue
        self.delayTime.set("Time: " + str(format(delayValue, '.6g')) + " seconds")

        print("Done")
        sleep(.1)
        clientSocket.close()
        fileRead.close()




    ######## Function:
    ######## wait_ack_0
    #### Purpose:
    #### one of the two states in this state machine,
    #### waits for ack 0 then sends next packet and goes to next state
    ## Paramters:
    ## prevpkt - previous packet for potential resending
    def wait_ack_0(self, prevpkt, clientSocket):
        #if corrupt or wrong sn resend
        rcvpkt = rdt_rcv(clientSocket)
        print(rcvpkt)
        while(CheckChecksum(rcvpkt)==False or IsAck(rcvpkt,0)==True):
            udt_send(prevpkt, clientSocket, ServerPort)
            rcvpkt = rdt_rcv(clientSocket)
            if(randint(0,100) < int(self.ackCor.get())):
                rcvpkt = CorruptPacket(rcvpkt)

    ######## Function:
    ######## wait_ack_1
    #### Purpose:
    #### one of the two states in this state machine,
    #### waits for ack 1 then sends next packet and goes to next state
    ## Paramters:
    ## prevpkt - previous packet for potential resending
    def wait_ack_1(self, prevpkt, clientSocket):
        # if corrupt or wrong sn resend
        rcvpkt = rdt_rcv(clientSocket)
        print(rcvpkt)
        while (CheckChecksum(rcvpkt) == False or IsAck(rcvpkt, 1) == True):
            udt_send(prevpkt, clientSocket, ServerPort)
            rcvpkt = rdt_rcv(clientSocket)
            if(randint(0,100) < int(self.ackCor.get())):
                rcvpkt = CorruptPacket(rcvpkt)

    def Init_PBar(self):
        self.pBar["value"]=(0)
        self.update_idletasks()

    def Update_PBar(self):
        self.pBar["value"] = (self.percentBytes)
        self.update_idletasks()



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
root.geometry("360x100+25+25")
# Run the tkinter GUI app
app.mainloop()
