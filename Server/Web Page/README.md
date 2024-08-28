# Exoskeleton Website Log
- html (folder): Front End of the websites (html files for websites)
- static (folder): Where css and javascripts are
- nginx (folder): Files for Nginx (will be in a different directory when actually being used to run Web page)
- backend (folder): Where python codes for backend is. This is where you will also find the updated data files.

# Server Instruction
## Nginx
1. Check if nginx is running `sudo systemctl status nginx`
2. Start Ngix if not `sudo systemctl start nginx` or `sudo systemctl restart nginx`
3. Check Firewall status `sudo ufw status` and open the ports if needed `sudo ufw allow 'Nginx Full'`
4. If the server seems to be missing some files or if you can't edit certain files, check ownership `ls -l /directory`
5. Change ownership `sudo chown -R user /directory`
6. Reload Ngnix `sudo systemctl reload nginx`

## Flask
1. Activate virtual space `source myenv/bin/activate`
2. Navigate to the folder with the Flask code `cd /var/www for Exoskeleton server pi`
3. Run the Flask code, app.py, `gunicorn -w 4 -b 127.0.0.1:8000 app:app` for data fetch
4. If it throws error `[ERROR] Connection in use` Try killing the process at port 8000. If there is no such process in the port wait few minutes then try running step 3. Otherwise, try using a different port `gunicorn -w 4 -b 127.0.0.1:8010 app:app`. When you do this, make sure you change the port in the default file too `under nginx/sites-available, proxy_pass address`
5. Deactivate once done (^C key)
