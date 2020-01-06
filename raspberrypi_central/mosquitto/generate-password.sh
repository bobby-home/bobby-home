# -c = user
sudo docker run -it --rm -v $PWD/config:/mosquitto/config eclipse-mosquitto mosquitto_passwd -c /mosquitto/config/passwd mx
