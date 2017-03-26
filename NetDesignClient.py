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
from time import clock, sleep
from threading import *

global root
global fileRead
global seqNum

FILE_ENDG   = 2
FILE_CURR   = 1
FILE_STRT   = 0

# Indexe numbers in thread dictionary tuple
IndexTimer  = 1
IndexStartT = 0

class App(Frame):
    # Tkinter initializing
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("File Transfer Tool")
        self.grid(sticky=E+W+N+S)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        # ------- V A R I A B L E   I N I T S -------

        self.currentPkts    = {} # Dictionary of current thread IDs. Future-proofing.
        self.threadMutex    = RLock()  # mutex for pkt dict control
        self.estimatedRTT   = DefaultRTT
        self.devRTT         = DefaultDev
        self.seqNum         = 0

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
        packdat = fileRead.read(PacketSize) #packet creation
        delayValue = clock() #start timer for overall transaction

        while((packdat != b'')):
            sndpkt = PackageHeader(packdat, self.seqNum, int(self.dataCor.get()))
            udt_send(sndpkt, clientSocket, ServerPort)  #begin state machine by entering wait ack 0 state

            self.threadMutex.acquire() # Lock to block other threads
            self.currentPkts[self.seqNum] = [  # Add entry into dictionary containing current time and the timout thread ID
                clock(),
                Timer(  # Start timeout counter by calling a new thread
                    self.estimatedRTT + (4) * (self.devRTT), self.Timeout,
                    args=[sndpkt, clientSocket, ServerPort]),  # arguments for Timeout()
                ]
            self.currentPkts[self.seqNum][IndexTimer].start()

            self.threadMutex.release()  # Release to allow other threads to modify

            rcvpkt = rdt_rcv(clientSocket)
            rcvpkt = CorruptCheck(rcvpkt, int(self.ackCor.get()))
            while (CheckChecksum(rcvpkt) == False or IsAck(rcvpkt, self.seqNum) == False): # if corrupt or wrong sn wait
                print(CheckChecksum(rcvpkt))
                rcvpkt = rdt_rcv(clientSocket)
                print(self.seqNum)
                print(rcvpkt)
                seed()
                rcvpkt = CorruptCheck(rcvpkt, int(self.ackCor.get()))

            self.EndTimeout() # Stop timeout
            self.seqNum = (self.seqNum + 1) % 2   # seqNum increments, but can only be 0 or 1

            packdat = fileRead.read(PacketSize)
            self.percentBytes = 100*(fileRead.seek(0, FILE_CURR)/self.maxBytes) - 1 # Update current place in file on progress bar
            self.Update_PBar()
        sndpkt = PackageHeader(packdat, self.seqNum) # Send a final message to the server to signify end
        udt_send(sndpkt, clientSocket, ServerPort)

        delayValue = clock() - delayValue
        self.delayTime.set("Time: " + str(format(delayValue, '.6g')) + " seconds")

        print("Done")
        sleep(.1)
        clientSocket.close()
        fileRead.close()

    # -------------------------------- T I M E O U T   F U N C T I O N S --------------------------------

    # Function to be pointed to be Timer() thread creation. Will activate after RTT unless cancelled by being acked.
    #If not cancelled before RTT, will resend the packet, create a new thread, and update the dictionary of thread
    #IDs with this new thread.
    def Timeout(self, sndPkt, clientSocket, ServerPort):
        #print("Making Timeout", int(clock()))
        self.threadMutex.acquire()  # Lock to block other threads

        udt_send(sndPkt, clientSocket, ServerPort)
        self.currentPkts[self.seqNum] = [  # Add entry into dictionary containing current time and the timout thread ID
            clock(),
            Timer(  # Start timeout counter by calling a new thread
                self.estimatedRTT + (4) * (self.devRTT), self.Timeout,
                args=[sndPkt, clientSocket, ServerPort]),  # arguments for Timeout()
        ]
        self.currentPkts[self.seqNum][IndexTimer].start()

        #print('Making Timeout')
        self.threadMutex.release()  # Release to allow other threads to modify

    def EndTimeout(self):
        curTime = clock()
        self.threadMutex.acquire()  # Lock to block other threads

        sampleRTT = curTime - self.currentPkts[self.seqNum][IndexStartT]
        self.currentPkts[self.seqNum][IndexTimer].cancel()  # Stop the timeout timer
        self.estimatedRTT = (1 - Alpha)*self.estimatedRTT + (Alpha * sampleRTT)
        self.devRTT = (1 - Beta)*self.devRTT + Beta*abs(sampleRTT - self.estimatedRTT)
        self.currentPkts.pop(self.seqNum, None)  # Remove dictionary key for seqNum, or do nothing if key DNE

        self.threadMutex.release()  # Release to allow other threads to modify

    # -------------------------------- T K I N T E R   F U N C T I O N S --------------------------------

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
root.geometry("340x100+25+25")
# Run the tkinter GUI app
app.mainloop()
