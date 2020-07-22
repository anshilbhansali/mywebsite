FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx
RUN apt-get install -y nano curl htop
RUN pip3 install uwsgi

COPY ./ ./app
WORKDIR ./app

RUN pip3 install -r requirements.txt

COPY ./nginx.conf /etc/nginx/sites-available/default

# Run the uwsgi server, and run the nginx server as a reverse proxy for the uwsgi server
# The proxy is done via the unix socket
# run uwsgi server with configurations in ini file
CMD service nginx start && uwsgi --ini app.ini
