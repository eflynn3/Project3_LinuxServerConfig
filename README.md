# Project 3 - Linux Server 
## Erin Flynn

* IP Address: 52.12.199.107
	* SSH port 2200
* URL for web app: http://52.12.199.107/
* Software installed:
	* postgresql
	* libapache2-mod-wsgi
	* apache2
	* flask
	* httplib2
	* sqlalchemy
* Linux Configuration Changes:
	* Denied connections on port 22
	* Allowed connections on 2200, www, ntp
	* In sshd_config, turned PermitRootLogin to no
	* Added new user called grader with sudo access
	* Added public key to the server for ssh with key
* Third party resources:
	* https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
	* https://www.bogotobogo.com/python/Flask/Python_Flask_HelloWorld_App_with_Apache_WSGI_Ubuntu14.php
