sudo pkill -f uwsgi -9
sudo service nginx restart
sudo nohup uwsgi --ini app.ini &
