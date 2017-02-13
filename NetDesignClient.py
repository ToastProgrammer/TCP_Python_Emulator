#Eric Craaybeek, Ben Tozier
#Python Net Design Project Phase 1

#code adapted from :
#"Computer Networking: A Top-Down Approach" by Keith Ross and James Kurose

from socket import *
from tkinter import *


global root

# Size of packets to send
PacketSize = 1024
# Message to signify end of file
TerminateCharacter = b''

ServerName = 'localhost'
# Port for socket to attach to
ServerPort = 12000

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

        # Setup socket
        clientSocket = socket(AF_INET, SOCK_DGRAM)

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
        fileRead.close()
        clientSocket.close()

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
