Team Members: 
 Eric Craaybeek, Ben Tozier

Files contained:
 readme.txt - this file
 NetDesignServer.py - the server file that receives the file
 NetDesignClient.py - the client file that sends a file
 DataFunctions.py - a file containing various functions used in packet manipulation
 SocketFunctions.py - a file containing modified send and receive functions
 Constants.py - a file containing various constants used in other parts of program
 design.docx - a descriptive document overviewing this project
 srcPic.png - picture file used to demonstrate file transfer
 srcPic2.png - second picture file for redundancy
 
Steps Required to execute:
 1: Ensure python is installed
 2: To send to the same machine leave the programs as is
 3: Open cmd, (or terminal) and navigate to the location of the program files
 4: Run the server by typing "python NetDesignServer.py"
 5: This window should read "The Server is ready to Receive"
 6: Open second cmd and repeat step 2
 7: Run the client by typing "python NetDesignClient.py"
 8: A GUI will appear asking for a filename.
 9: Type srcPic.png (or any other filename in this folder including srcPic2.bmp)
 10: Press enter
 11: The server should receive the file and write it to dstPic.png
 12: To simulate Data or Ack packet bit error, simply change their relative percentages in the UI
