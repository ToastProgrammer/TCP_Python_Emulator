 Team Members: 
 Eric Craaybeek, Ben Tozier

Files contained:
 readme.txt - this file
 NetDesignServer.py - the server file that receives bytes and sends them back
 NetDesignClient.py - the client file that sends a file called testRead.txt
 design.docx - a descriptive document overviewing this project
 srcPic.png - picture file used to demonstrate file transfer
 srcPic2.png - second picture file for redundancy
 
Steps Required to execute:
 1: Ensure python is installed
 2: To send to the same machine leave the programs as is;
    To send to a different machine edit NetDesignClient.py and change the servername variable
    to the address of the machine that the server will run on.
 3: Open cmd, (or terminal) and navigate to the location of the program files
 4: Run the server by typing "python NetDesignServer.py"
 5: This window should read "The Server is ready to Receive"
 6: Open second cmd and repeat step 2
 7: Run the client by typing "python NetDesignClient.py"
 8: A GUI will appear asking for a filename.
 9: Type srcPic.png (or any other filename in this folder including srcPic2.png)
 10: Press enter
 11: The server should receive testRead, send it back, and the client writes this to testWrite.txt
