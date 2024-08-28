# File Explanation:
- constants.py: Used to store constants that can be changed according to devices/purposes. What you wouls ba changing if you are trying to use this on your own devices
- main.py: File to execute to run the client. This executes the other 2 python scripts (execCommands.py and updateData.py) on different threads to enable 2 way communication.
- execCommands.py: Recieves command from server, classify them, and control servant arduinos accordingly. To add more functions, update this file (update the while loop to handle the new case (eg. `if (command[0] == 'newMethodTrigger'): ...`), and add a new method (eg. `def newMethodTrigger(command): ...`) under existing methods).
- updateData.py: Sends the data to the server. To send the file, the file must be in the same folder with the python codes, and name & type of the file has to be updated in the constants.py file. THIS CODE DOES NOT HAVE TO BE MODIFIED TO SEND DIFFERENT FILES
- dummy.txt/large.csv/small.csv: A test file to check file/data transmission between the servers
- Old Test Codes (folder): Any codes that I used in the middle to test simple parts out before integrating. You can ignore this folder if you just want to use the end product. (you can delete this on your end)
    
    
# Debug Log in Client Pi Codes
