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

SendFSMDict = {0: SendFSM0, 1:SendFSM1, 2:SendFSM2, 3:SendFSM3}
RecieveFSMDict = {0:RecvFSM0, 1:RecvFSM1}

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
        self.estimatedRTT   = DefaultRTT    # Initial EstimatedRTT
        self.devRTT         = DefaultDev    # Initial EstimatedRTTDeviation
        self.seqNum         = 0             # Initial Sequence number
        self.concurrentThreads = 0          # Number of threads - Main thread running | Debug

        # ----------- F S M   D i s p l a y s -----------
        self.sendFSMLabel = Label(root, text='Sender FSM')
        self.sendFSMLabel.grid(row=5, column=0, padx=40,  pady=1, sticky=W+S)

        self.sendFSM = Label()
        self.sendFSM.grid(row=6, column=0, pady=1, sticky=E+S)
        self.UpdateFSM(0, True) # Update the image of the Sender FSM

        self.recvFSMLabel = Label(root, text='Reciever FSM')
        self.recvFSMLabel.grid(row=5, column=1, padx=40, pady=1, sticky=E+S, columnspan = 2)

        self.recvFSM = Label()
        self.recvFSM.grid(row=6, column=1, padx=3, pady=1, sticky=E+S, columnspan = 2)
        self.UpdateFSM(0, False)    # Update the image of the Reciever FSM

        # ----------- T i m e   D i s p l a y -----------

        self.timeLabel = Label(root, text='Time taken:')
        self.timeLabel.grid(row=0, column=1, padx=3, pady=2, sticky=E+S)

        # ----------------
        self.delayTime = StringVar()
        self.delay = Label(root, textvariable = self.delayTime)
        self.delay.grid(row=0, column=2, padx=3, pady=2, sticky=W+N+S)
        self.delayTime.set('')

        # -------- D a t a   C o r r u p t i o n --------

        self.dataCorStr = Label(root, text='Data Error %:')
        self.dataCorStr.grid(row=1, column=1, padx=3, pady=2, sticky=E+S)
        # ----------------
        # Variable entry for % data corruption
        self.dataCorPercent = Entry()
        self.dataCorPercent.grid(row=1, column=2, padx=3, pady=2, sticky=W+S, columnspan=1)
        self.dataCor = StringVar()
        # Default contents of variable will be 0
        self.dataCor.set('0')
        # tell the entry widget to watch this variable
        self.dataCorPercent["textvariable"] = self.dataCor

        # --------- A c k   C o r r u p t i o n ---------

        self.ackCorStr = Label(root, text='ACK Error %:')
        self.ackCorStr.grid(row=2, column=1, padx=3, pady=2, sticky=E+S)
        # ----------------
        # Variable entry for % data corruption
        self.ackCorPercent = Entry()
        self.ackCorPercent.grid(row=2, column=2, padx=3, pady=2, sticky=W+S, columnspan=1)
        self.ackCor = StringVar()
        # Default contents of variable will be 0
        self.ackCor.set('0')
        # tell the entry widget to watch this variable
        self.ackCorPercent["textvariable"] = self.ackCor

        ## -------------- D a t a   L o s s --------------

        self.dataLossStr = Label(root, text='Data Loss %:')
        self.dataLossStr.grid(row=3, column=1, padx=3, pady=2, sticky=E+S)
        # ----------------
        # Variable entry for % data corruption
        self.dataLossPercent = Entry()
        self.dataLossPercent.grid(row=3, column=2, padx=3, pady=2, sticky=W+S, columnspan=1)
        self.dataLoss = StringVar()
        # Default contents of variable will be 0
        self.dataLoss.set('0')
        # tell the entry widget to watch this variable
        self.dataLossPercent["textvariable"] = self.dataLoss

        # --------------- A c k   L o s s ---------------

        self.ackLossStr = Label(root, text='Ack Loss %:')
        self.ackLossStr.grid(row=4, column=1, padx=3, pady=2, sticky=E+S)
        # ----------------
        # Variable entry for % data corruption
        self.ackLossPercent = Entry()
        self.ackLossPercent.grid(row=4, column=2, padx=3, pady=2, sticky=W+S, columnspan=1)
        self.ackLoss = StringVar()
        # Default contents of variable will be 0
        self.ackLoss.set('0')
        # tell the entry widget to watch this variable
        self.ackLossPercent["textvariable"] = self.ackLoss

        # ------------ S o u r c e   F i l e ------------

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

        # ----------- P r o g r e s s   B a r -----------

        self.percentBytes   = IntVar(self)
        self.maxBytes       = IntVar(self)

        self.pBar = ttk.Progressbar(self, orient = "horizontal",
                                    length = 150, mode = "determinate",
                                    value=0, maximum=100)
        self.pBar.grid(row=0, column=2, padx = 3, pady = 2, sticky=E+W+N, columnspan=3)

    # ------------------------------------ M A I N   F U N C T I O N ------------------------------------
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

        self.seqNum = 0
        packdat = fileRead.read(PacketSize) #packet creation
        delayValue = clock() #start timer for overall transaction

        while((packdat != b'')):
            self.UpdateFSM(self.seqNum *2 + 1, True)    # Update FSM diagram to "Wait ACK seqNum"
            sndpkt = PackageHeader(packdat, self.seqNum)
            udt_send(sndpkt, clientSocket, ServerPort,
                     corChance = int(self.dataCor.get()),
                     lossChance = int(self.dataLoss.get())
                     )  #begin state machine by entering wait ack 0 state
            #print(sndpkt)

            self.threadMutex.acquire() # Lock to block other threads
            self.currentPkts[self.seqNum] = [  # Add entry into dictionary containing current time and the timout thread ID
                clock(),
                Timer(  # Start timeout counter by calling a new thread
                    self.estimatedRTT + (4) * (self.devRTT), self.Timeout,
                    args=[sndpkt, clientSocket, ServerPort, int(self.dataCor.get()), int(self.dataLoss.get())]),  # arguments for Timeout()
                ]
            self.currentPkts[self.seqNum][IndexTimer].start()   # Initiate the new thread

            self.threadMutex.release()  # Release to allow other threads to modify

            rcvpkt = rdt_rcv(clientSocket)
            rcvpkt = CorruptCheck(rcvpkt, int(self.ackCor.get()))
            ackLoss = LossCheck(int(self.ackLoss.get()))    # Check to see if ack was "lost"
            while (ackLoss == True or CheckChecksum(rcvpkt) == False or IsAck(rcvpkt, self.seqNum) == False): # if corrupt or wrong sn wait
                rcvpkt = rdt_rcv(clientSocket)
                seed()
                rcvpkt = CorruptCheck(rcvpkt, int(self.ackCor.get()))
                ackLoss = LossCheck(int(self.ackLoss.get()))    # Check to see if ack was "lost"
            self.EndTimeout() # Stop timeout
            self.UpdateFSM(self.seqNum, False)
            self.UpdateFSM((self.seqNum + 2) % 3, True) # Update FSM diagram to "Wait for seqNum Above"
            self.seqNum = (self.seqNum + 1) % 2   # seqNum increments, but can only be 0 or 1

            packdat = fileRead.read(PacketSize)
            self.percentBytes = 100*(fileRead.seek(0, FILE_CURR)/self.maxBytes) - 1 # Update current place in file on progress bar
            self.Update_PBar()
        sndpkt = PackageHeader(packdat, self.seqNum) # Send a final message to the server to signify end
        udt_send(sndpkt, clientSocket, ServerPort, corChance = 0)

        delayValue = clock() - delayValue   # Calculate total time taken to transfer and display it
        self.delayTime.set("Time: " + str(format(delayValue, '.6g')) + " seconds")

        print("Done")
        sleep(.1)   # Wait to allow server to close first
        clientSocket.close()
        fileRead.close()

    # -------------------------------- T I M E O U T   F U N C T I O N S --------------------------------

    # Function to be pointed to be Timer() thread creation. Will activate after RTT unless cancelled by being acked.
    #If not cancelled before RTT, will resend the packet, create a new thread, and update the dictionary of thread
    #IDs with this new thread.
    def Timeout(self, sndPkt, clientSocket, ServerPort, corChance, lossChance):
        self.threadMutex.acquire()  # Lock to block other threads
        self.concurrentThreads += 1
        udt_send(sndPkt, clientSocket, ServerPort, corChance, lossChance)
        self.currentPkts[self.seqNum] = [  # Add entry into dictionary containing current time and the timout thread ID
            clock(),
            Timer(  # Start timeout counter by calling a new thread
                self.estimatedRTT + (4) * (self.devRTT), self.Timeout,
                args=[sndPkt, clientSocket, ServerPort, corChance, lossChance]),  # arguments for Timeout()
        ]
        self.currentPkts[self.seqNum][IndexTimer].start()

        self.threadMutex.release()  # Release to allow other threads to modify
        self.concurrentThreads -= 1 # Deincrement current threads as exit
        return  # exits thread

    def EndTimeout(self):
        curTime = clock()   # Immediately take clock first to get better RTT estimation
        self.threadMutex.acquire()  # Lock to block other threads
        if self.concurrentThreads != 0:
            print("Current Threads", self.concurrentThreads)    # Error Checking
        sampleRTT = curTime - self.currentPkts[self.seqNum][IndexStartT]
        self.currentPkts[self.seqNum][IndexTimer].cancel()  # Stop the timeout timer
        self.estimatedRTT = (1 - Alpha)*self.estimatedRTT + (Alpha * sampleRTT)
        self.devRTT = (1 - Beta)*self.devRTT + Beta*abs(sampleRTT - self.estimatedRTT)
        self.currentPkts.pop(self.seqNum, None)  # Remove dictionary key for seqNum, or do nothing if key DNE

        self.threadMutex.release()  # Release to allow other threads to modify

    # -------------------------------- T K I N T E R   F U N C T I O N S --------------------------------

    # Initiate progress bar to 0%
    def Init_PBar(self):
        self.pBar["value"]=(0)
        self.update_idletasks()

    # Update progress bar to percentage
    def Update_PBar(self):
        self.pBar["value"] = (self.percentBytes)
        self.update_idletasks()

    # Update either FSM graphic
    def UpdateFSM(self, state, isSender = True):
        if isSender:
            self.fileName = SendFSMDict[state]
        else:
            self.fileName = RecieveFSMDict[state]
        photo = PhotoImage(file=self.fileName)
        if isSender:
            self.sendFSM.configure(image=photo)
            self.sendFSM.image = photo
        else:
            self.recvFSM.configure(image=photo)
            self.recvFSM.image = photo
        self.update_idletasks() # Actually tell tkinter to update itself


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
root.geometry("365x320+25+25")
# Run the tkinter GUI app
app.mainloop()
