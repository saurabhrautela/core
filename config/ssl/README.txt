Use following commands to generate self-signed certificate and dh parameters:

openssl req -x509 -days -nodes -newkey rsa:4096 -keyout self.key -out self.crt
openssl dhparam -out /etc/nginx/ssl/dhparam.pem 4096

Use the above certificates only for local setup during development. For production, get certificates from https://letsencrypt.org/.
