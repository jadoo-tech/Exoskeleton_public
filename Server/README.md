# File/Folder Explanations
- Codes in Web Page is for the Exoskeleton webpage, which includes backend folder (Flask), html folder, static folder (css and js) and nginx folder (nginx setups)
      - constants.py: Used to store constants that can be changed according to devices/purposes. What you would be changing if you are trying to use this on your own devices
- Old Test Codes (folder): Any codes that I used in the middle to test simple parts out before integrating. You can ignore this folder if you just want to use the end product. (you won't need this file at all)
    - Codes in Raspberry Pi are the codes needed on the Server pi, to operate as a server.
### Old Test Codes:
- If the whole Webpage - pi - arduino system is not working for some reason, try testing the server <-> pi system using the code under Raspberry Pi folder. This codes share the same logic used in the web <-> pi communication. If this works fine, the problem would be either web (Flask or Ngnix) or Client (pi <-> arduino communication)
    
# Debug Steps in Using
To use from a different pi:
1. type ifconfig to terminal, and change HOST in constants.py to the IP address (under wlan0)
2. If timeout error occurs on the client end but it works fine on the server, try: sudo ufw allow 9158/tcp on the server terminal to allow firewall to access the port from external device.
3. Check status of firewall by sudo ufw status
4. (When working in Stanley lab with visitor wifi) Open browser and try accessing any link to make sure you are connected.

# Ngnix Installation guide:
To install Ngnix at the server pi:
1. ```git readme code block```
2. ```sudo apt install nginx```
3. ```
   sudo systemctl start nginx
   sudo systemctl enable nginx
4. ```sudo systemctl status nginx```
5. Install ufw

# Package List
1. Ngnix
2. Flask
3. Yolo
4. gunicorn
5. UFW
