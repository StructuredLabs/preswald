#!/bin/bash

DOMAIN_NAME=<YOUR-DOMAiN.TLD>
EMAIL=<YOUR-EMAIL>

set -e

sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y

# install docker
if ! command -v docker >/dev/null 2>&1; then
	sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y
	sudo apt update
	sudo apt install docker-ce -y
fi

echo "HERE"

# Start docker
sudo systemctl enable docker
sudo systemctl start docker

# Install nginx
if ! command -v nginx >/dev/null 2>&1; then
	sudo apt install nginx -y
fi

sudo rm -f /etc/nginx/sites-available/app
sudo rm -f /etc/nginx/sites-enabled/app

sudo systemctl stop nginx

# Obtain SSL certificate using Certbot standalone mode
sudo apt install certbot -y
sudo certbot certonly --standalone -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos -m $EMAIL

# Ensure SSL files exist or generate them
if [ ! -f /etc/letsencrypt/options-ssl-nginx.conf ]; then
	sudo wget https://raw.githubusercontent.com/certbot/certbot/main/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf -P /etc/letsencrypt/
fi

if [ ! -f /etc/letsencrypt/ssl-dhparams.pem ]; then
	sudo openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048
fi

# Create Nginx config with reverse proxy, SSL support, rate limiting, and streaming support
sudo cat > /etc/nginx/sites-available/app <<EOL
limit_req_zone \$binary_remote_addr zone=mylimit:10m rate=30r/s;

server {
	listen 80;
	server_name $DOMAIN_NAME www.$DOMAIN_NAME;

	# Redirect all HTTP requests to HTTPS
	return 301 https://\$host\$request_uri;
}

server {
	listen 443 ssl;
	server_name $DOMAIN_NAME www.$DOMAIN_NAME;

	ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;
	include /etc/letsencrypt/options-ssl-nginx.conf;
	ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

	# Enable rate limiting
	limit_req zone=mylimit burst=40 nodelay;

	client_max_body_size 1024M;

	location / {
		proxy_pass http://localhost:8501;
		proxy_http_version 1.1;
		proxy_set_header Upgrade \$http_upgrade;
		proxy_set_header Connection 'upgrade';
		proxy_set_header Host \$host;
		proxy_cache_bypass \$http_upgrade;

		# Disable buffering for streaming support
		proxy_buffering off;
		proxy_set_header X-Accel-Buffering no;
	}
}
EOL

# Create symbolic link if it doesn't already exist
sudo ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app

# Restart Nginx to apply the new configuration
sudo systemctl restart nginx

# Stop any running containers on port 8501
docker ps -q --filter "publish=8501" | xargs -r docker stop

# Build and run the Docker containers from the app directory
sudo docker build -t testing_preswald_image .
sudo docker run -p 8501:8501 -d testing_preswald_image

# Check if container is running
if ! sudo docker ps | grep "Up"; then
	echo "Docker containers failed to start. Check logs with 'docker-compose logs'."
	exit 1
fi

# Output final message
echo "Deployment complete. Your Preslaw app is available at https://$DOMAIN_NAME :)"

exit 0