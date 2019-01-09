#!/usr/bin/env bash

## README !!

# Warning, when you curl on localhost:80, you should get a refused if nothing is listening
# Steps : 
	# On Azure portal : open port 80 through the security group
	# Warning, if you curl localhost at this point, it should still be refused !
	# Install NGINX at this point with (i)   listen 80; and (ii) proxy_pass http://127.0.0.1:8000; 
	# Your network application (website / API) should listen on 8000 and send responses
	# On the server (i) curl localhost:80 should be OK (ii) curl localhost:8000 should be OK 
	# Remotely (i) curl localhost:80 should be OK (ii) curl localhost:8000 should be not OK
##

echo "Setting up Nginx on port 80 "
sudo apt-get -y install nginx

sudo service nginx start
FILE="/etc/nginx/sites-available/inwibeapi"
FILE2="/etc/nginx/sites-enabled/inwibeapi"
sudo rm $FILE -enabled
sudo rm $FILE2 -f

sudo /bin/cat <<EOM >$FILE
server {
  listen 80 default_server;
  server_name inwibeapi;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  }

  location /static {
    alias /code/inwibe/inwibe/ressources
}
}
EOM

cd /etc/nginx/sites-enabled
sudo ln -s ../sites-available/inwibeapi
sudo rm default
sudo service nginx reload
sudo service nginx restart