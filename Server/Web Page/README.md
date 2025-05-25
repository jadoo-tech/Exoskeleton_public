# Exoskeleton Website Log
- html (folder): Front End of the websites (html files for websites)
- static (folder): Where css and javascripts are
- nginx (folder): Files for Nginx (will be in a different directory when actually being used to run Web page)
- backend (folder): Where python codes for backend is. This is where you will also find the updated data files.

# Server Instruction
## Nginx
1. Check if nginx is running `sudo systemctl status nginx`
2. Start Ngix if not `sudo systemctl start nginx` or `sudo systemctl restart nginx`
3. Check Firewall status `sudo ufw status` and open the ports if needed `sudo ufw allow 'Nginx Full'` If its not active run ```sudo ufw enable```
4. If the server seems to be missing some files or if you can't edit certain files:
       1. check ownership `ls -l /directory`
       2. Change ownership `sudo chown -R user /directory`
       3. Reload Ngnix `sudo systemctl reload nginx`
5. Replace the nginx at etc/ngnix file with the nginx folder in this repo.
6. Move the static, backend, and html folder to var/www/ folder. 

## Flask
1. Navigate to the folder: `cd /var/www` and activate virtual space `source myenv/bin/activate`
2. Navigate to the folder with the Flask code. `cd /var/www/backend` for Exoskeleton server pi
3. Run the Flask code, app.py, `gunicorn -w 1 -b 127.0.0.1:8000 app:app` for data fetch. If it doesnt work, try `export PYTHONPATH=.
   gunicorn -w 1 -b 127.0.0.1:8000 app:app`
5. If it throws error `[ERROR] Connection in use` Try killing the process at port 8000. If there is no such process in the port wait few minutes then try running step 3. Otherwise, try using a different port `gunicorn -w 1 -b 127.0.0.1:8010 app:app`. When you do this, make sure you change the port in the default file to `under nginx/sites-available, proxy_pass address`
   1. If the address does not connect, check the host address with `ifconfig -a`. Should be with wan0.
6. Deactivate once done (^C key)
   ### ERRORS & DEBUGGING STEPS ###
   #### `OSError: [Errno 98] Address already in use` ####
   1. Check if something is using the port: `sudo lsof -i :<PORT>` and kill the operation if there is something running
   2. 

## Libraries used:
- `pip install opencv-python`
- `pip install flask`
- `pip install guinicorn`
