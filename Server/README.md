# File/Folder Explanations
- Codes in Raspberry Pi are the codes needed on the Server pi, to operate as a server.
- Codes in Web Page is for the Exoskeleton webpage, and can be ignored
    
# Degug Steps Taken:
1. type ifconfig to terminal, and change HOST in constants.py to the IP address (under wlan0)
2. If timeout error occurs on the client end but it works fine on the server, try sudo ufw allow 9158/tcp on the server terminal to allow firewall to access the port from external device.
