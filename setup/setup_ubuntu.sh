sudo apt-get install git-all
sudo apt-get install -y python3 python3-dev python3-pip nginx
sudo apt-get install -y nano curl htop
sudo pip3 install uwsgi
sudo pip3 install -r requirements.txt
sudo cp nginx.conf /etc/nginx/sites-available/default

# SSL
sudo add-apt-repository ppa:certbot/certbot
