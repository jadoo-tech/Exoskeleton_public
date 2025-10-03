# File Descriptions
- app.py: main flask file that runs in the backend. Handles data fetch, sending out commands through web socket, etc.
- constants.py: Used to store constants that can be changed according to devices/purposes. What you would be changing if you are trying to use this on your own devices
- data.csv: The file that is currently being displayed in the webpage. Because simultaneous modification is impossible, we have to change this to SQL and allow reading and modifying the document at the same time. Does not currently get updates from the client pi
- recvFile.py: Code for getting updates of data.csv file from server. app.py has to run this on a different thread to enable 2 way communication, but is not currently implemented on app.py file.
