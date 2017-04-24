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

# --------------------------------- G L O B A L   V A R I A B L E S ---------------------------------

global root
global fileRead
transDone = False

srcFile = 's.bmp'

nextSeqNum          = 1             # Initial Sequence number
base                = 1
finalPacket         = None

connBreakThread     = None
timer               = []
devRTT              = DefaultDev    # Initial EstimatedRTTDeviation
estimatedRTT        = DefaultRTT    # Initial EstimatedRTT

currentPackets      = {}
sndpkt              = [0]

threadMutex         = RLock()  # mutex for pkt dict control
baseMutex           = RLock()
pktMutex            = RLock()

pktsReadySemaphore  = Semaphore(0)



concurrentThreads  = 0          # Number of threads - Main thread running | Debug


# -------------------------------- C O N S T A N T S   D E F I N E S --------------------------------
FILE_ENDG   = 2
FILE_CURR   = 1
FILE_STRT   = 0

# Indexe numbers in thread dictionary tuple
IndexTimer  = 1
IndexStartT = 0

SizeTimerStruct = 2

SendFSMDict = {0: SendFSM0, 1:SendFSM1, 2:SendFSM2, 3:SendFSM3}
RecieveFSMDict = {0:RecvFSM0, 1:RecvFSM1}

#============================== F U N C T I O N S ==============================
#====================================== = ======================================
#---------------------------------------- --------------------------------------

#======================== T h r e a d   F u n c t i o n s ======================

#---------------------------- T k i n t e r   A p p ----------------------------

class App(Frame):
    # Tkinter initializing
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("File Transfer Tool")
        self.grid(sticky=E+W+N+S)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        # ----------- F S M   D i s p l a y s -----------
        self.sendFSMLabel = Label(root, text='Sender FSM')
        self.sendFSMLabel.grid(row=5, column=0, padx=40, pady=1, sticky=W + S)

        self.sendFSM = Label()
        self.sendFSM.grid(row=6, column=0, pady=1, sticky=E + S)
        self.UpdateFSM(0, True)  # Update the image of the Sender FSM

        self.recvFSMLabel = Label(root, text='Reciever FSM')
        self.recvFSMLabel.grid(row=5, column=1, padx=40, pady=1, sticky=E + S, columnspan=2)

        self.recvFSM = Label()
        self.recvFSM.grid(row=6, column=1, padx=3, pady=1, sticky=E + S, columnspan=2)
        self.UpdateFSM(0, False)  # Update the image of the Reciever FSM

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
        self.dataCor.set('10')
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
        self.ackCor.set('10')
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
        self.dataLoss.set('10')
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
        self.ackLoss.set('10')
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
        self.maxBytes       = 1000000000

        self.pBar = ttk.Progressbar(self, orient = "horizontal",
                                    length = 150, mode = "determinate",
                                    value=0, maximum=100)
        self.pBar.grid(row=0, column=2, padx = 3, pady = 2, sticky=E+W+N, columnspan=3)

        # -------------------------------- T K I N T E R   F U N C T I O N S --------------------------------
        # Initiate progress bar to 0%
        def Init_PBar(self):
            self.pBar["value"] = (0)
            self.update_idletasks()

        # Update progress bar to percentage
        def Update_PBar(self):
            self.pBar["value"] = (self.percentBytes)
            self.update_idletasks()

        # Update either FSM graphic
        def UpdateFSM(self, state, isSender=True):
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
            self.update_idletasks()  # Actually tell tkinter to update itself

        ######## Function:
        ######## Quit
        #### Purpose:
        #### Quit and close tkinter GUI window on error
        ## Paramters:
        ## None
        def Quit(self):
            root.destroy()

#------------------------------ S e n d _ F i l e ------------------------------

def send_file():

    global clientSocket

    global connBreakThread

    global transDone

    global base
    global nextSeqNum
    global finalPacket

    transDone = False  # variable to notify

    if connBreakThread is not None:     # If previous connection run
        if connBreakThread.is_alive():  # If previous teardown still in effect, cancel it
            connBreakThread.cancel()

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', ClientPort))

    sendingThread   = Thread(None, SendThread, "Sending Thread")

    recieveThread   = Thread(None, RecieveThread, "Recieving Thread")  # Initialize Recieve Thread

    packingThread   = Thread(None, PackingThread, "Packet-Making Thread")

    delayValue = clock() #start timer for overall transaction

    started = False

    # Initialize sending, recieving, and packing threads
    sendingThread.start()
    recieveThread.start()
    packingThread.start()

    packingThread.join()
    print("Packing Thread Joined************************")
    recieveThread.join()  # wait for recieve thread to conclude
    print("Recieving Thread Joined*************************")
    sendingThread.join()
    print("Sending Thread Joined*************************")

    StartConnTeardown()

    # Reset some values to default
    finalPacket = None
    base = 0
    nextSeqNum = 0

    print("Send another?")

#---------------------------- S e n d   T h r e a d ----------------------------

def SendThread():
    if True:
        global clientSocket

        global pktMutex
        global threadMutex
        global pktsReadySemaphore

        global finalPacket
        global base
        global nextSeqNum

        global sndpkt   # Dictionary of ready packets

        global transDone

        global delayValue

    delayValue = clock()

    while((finalPacket == None) or (finalPacket != nextSeqNum-1)):
        baseMutex.acquire()
        if (nextSeqNum < base+WindowSize and len(sndpkt) > nextSeqNum - 1): #If next sequence number in window
            print("Gettting pktsReady")
            pktsReadySemaphore.acquire()
            print("Got pktsReady")
            udt_send(sndpkt[nextSeqNum], clientSocket, ServerPort, dataCorChance, dataLossChance)

            if (base == nextSeqNum):
                StartTimeout(wasAcked=False)
            nextSeqNum += 1
            print("Senders nextSequNum", nextSeqNum)
        baseMutex.release()

    while(base != finalPacket+1):
        pass
    transDone = True   # Signal recieve thread of completion

    delayValue = clock() - delayValue   # Calculate total time taken to transfer and display it

    EndTimeout(False)

    sleep(.1)   # Wait to allow server to close first


#-------------------------- R e c i e v e   T h r e a d ------------------------

def RecieveThread():
    if True:

        global clientSocket

        global pktMutex
        global threadMutex

        global connBreakThread

        global finalPacket
        global base
        global nextSeqNum

        global sndpkt  # Dictionary of ready packets

        global transDone    # Global bool to communicate status of transmission between threads


    while(transDone == False):
        rcvpkt = rdt_rcv(clientSocket)
        rcvpkt = CorruptCheck(rcvpkt, ackCorChance)
        ackLoss = LossCheck(ackLossChance)  # Check to see if ack was "lost"
        print("Reciever got", rcvpkt[IndexSeqNum])
        if (ackLoss == False and CheckChecksum(rcvpkt) == True and CheckHigherSeq(rcvpkt,base)):
            baseMutex.acquire()
            base = GetSequenceNum(rcvpkt)
            print("New Base =", base, "Next Seq =", nextSeqNum)
            baseMutex.release()
            if base == nextSeqNum:
                EndTimeout(wasAcked=True)
                print("Do I ever get here?")
            else:
                StartTimeout(wasAcked=True)

            #print("Recievethread nextSeqNum:",nextSeqNum)
    transDone = False   # Reset for next transfer
#-------------------------- P a c k i n g   T h r e a d ------------------------
def PackingThread():

    if True:
        global srcFile
        global clientSocket

        global pktMutex
        global threadMutex
        global pktsReadySemaphore

        global finalPacket
        global base
        global nextSeqNum

        global sndpkt  # Dictionary of ready packets

        global transDone

        global delayValue

    i = 1
    looped = False

    # Procedure to automatically close window if invalid file is given
    try:
        fileRead = open(srcFile, "rb")
    except FileNotFoundError:
        print(srcFile, "not found")
        #self.Quit()
        raise
    except:
        #self.Quit()
        raise

    #maxBytes = fileRead.seek(0, FILE_ENDG)  # Get total # of bytes in file and set as roof for progress bar
    fileRead.seek(0, FILE_STRT)  # Reset file position

    packdat = fileRead.read(PacketSize)  # packet creation

    pktMutex.acquire()
    while ((packdat != b'')):
        if looped == False:
            sndpkt.append(PackageHeader(packdat, i))
        else:
            sndpkt[i] = PackageHeader(packdat, i)
        pktsReadySemaphore.release()    # signal sending thread that it can proceed
        packdat = fileRead.read(PacketSize)  # packet creation
        i += 1
        if i > 255:
            i = 1
            looped = True

    if looped == False:
        sndpkt.append(PackageHeader(b'', i, fin=True))    # final packet
    else:
        sndpkt[i] = PackageHeader(b'', i, fin=True)

    pktsReadySemaphore.release()    # Post the semaphore for the final packet

    finalPacket = i     # Set the global final packet so that other threads can see
    print("FINAL PACKET IS ", i)
    pktMutex.release()
    fileRead.close()

#====================== T i m e o u t   F u n c t i o n s ======================


#---------------------------- S t a r t T i m e o u t --------------------------

def StartTimeout(wasAcked):

    global timer
    if len(timer) == SizeTimerStruct:
        print("Deleted Prev Timer")
        EndTimeout(wasAcked)    #end any previous timeouts going

    global threadMutex
    threadMutex.acquire()  # Lock to block other threads
    global estimatedRTT
    global devRTT

    localTimer = Timer( estimatedRTT + (4) * (devRTT), Timeout)
    print("Timer val = ", estimatedRTT + 4*devRTT)

    if len(timer) == SizeTimerStruct:
        timer[IndexStartT] = clock()
        timer[IndexTimer] = localTimer
    else:
        timer.append(clock())
        timer.append(localTimer)

    threadMutex.release()  # Release to allow other threads to modify
    timer[IndexTimer].start()  # Initiate the new thread


#-------------------------------- T i m e o u t --------------------------------
def Timeout():

    global baseMutex
    global threadMutex
    threadMutex.acquire()
    aquired = baseMutex.acquire(timeout = estimatedRTT + 4*devRTT)

    global base
    global nextSeqNum
    global finalPacket

    global sndpkt
    global clientSocket

    print("Started timer")
    i = base
    if aquired:
        baseMutex.release()
    while i < nextSeqNum+1:
        #print("Timeout Packet sent:", i)
        try:
            tempsend = sndpkt[i]
            print(i, tempsend[IndexSeqNum])
            udt_send(tempsend, clientSocket, ServerPort,
                 dataCorChance,
                 dataLossChance
                 )
            if i == finalPacket:
                print("SENDING FINAL PACKET")
        except:
            pass
        i+=1
    print("Sent from", base, nextSeqNum)
    threadMutex.release()
    StartTimeout(wasAcked = False)
    return  # exits thread

#------------------------------ E n d T i m e o u t ----------------------------
def EndTimeout(wasAcked):

    curTime = clock()  # Immediately take clock first to get better RTT estimation
    print("Ending Timer")
    global threadMutex
    threadMutex.acquire()  # Lock to block other threads


    global timer
    global estimatedRTT
    global devRTT

    timer[1].cancel()  # Stop the timeout timer
    if wasAcked:
        sampleRTT = curTime - timer[0]
        estimatedRTT = (1 - Alpha)*estimatedRTT + (Alpha * sampleRTT)
        devRTT = (1 - Beta)*devRTT + Beta*abs(sampleRTT - estimatedRTT)

    threadMutex.release()  # Release to allow other threads to modify

def StartConnTeardown():

    global base
    global clientSocket

    # Start Connection Breakdown
    connBreakPkt = PackageHeader(ACK, base, fin=True)  # Server FIN ACK packet
    connBreakThread = Thread(None, ConnectionBreakdown, "Connection Breakdown Thread", args=[connBreakPkt])
    finRecieved = False
    print("Before breakdown loop")
    while (finRecieved == False):

        rcvpkt = rdt_rcv(clientSocket)
        print("Waited")
        print(rcvpkt[0:6])
        rcvpkt = CorruptCheck(rcvpkt, ackCorChance)
        ackLoss = LossCheck(ackLossChance)

        if (CheckFin(rcvpkt) and ackLoss == False and CheckChecksum(rcvpkt)):
            udt_send(connBreakPkt, clientSocket, ServerPort, corChance=dataCorChance, lossChance=dataLossChance)
            connBreakThread.start()
            finRecieved = True

#-------------------- C o n n e c t i o n   B r e a k d o w n ------------------
def ConnectionBreakdown(connBreakPkt):

    global clientSocket

    clientSocket.settimeout(1.0)
    startT = clock()
    while(True):
        try:
            rcvpkt = rdt_rcv(clientSocket)  # socket timeout raises exception
            rcvpkt = CorruptCheck(rcvpkt, ackCorChance)
            ackLoss = LossCheck(ackLossChance)

            if (CheckFin(rcvpkt) and ackLoss == False and CheckChecksum(rcvpkt)):

                udt_send(connBreakPkt, clientSocket, ServerPort, corChance=dataCorChance, lossChance=dataLossChance)

            newTimeout = 30.0 - (clock() - startT)  # Get amount of time since "30 seconds" started
            if(newTimeout < 0): # If time went over while responding
                break
            clientSocket.settimeout(newTimeout) # Total timeout must be around  accumulative 30 seconds
        except:
            pass






        #root = Tk()
#app = App(master=root)
#root.geometry("365x320+25+25")
## Run the tkinter GUI app
#app.mainloop()

send_file()