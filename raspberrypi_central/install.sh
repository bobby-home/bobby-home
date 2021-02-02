#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git vim libffi-dev libssl-dev python python-pip python3-pip

sudo apt install -y ipcalc nmap git vim libffi-dev libssl-dev python python-pip python3-pip pipenv

# Docker
sudo apt-get remove -y python-configparser
sudo apt-get -y install python3-pip
sudo pip3 install docker-compose

sudo apt autoremove

curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi

# enable the pi camera.
sudo raspi-config nonint do_camera 0

docker network create --gateway 172.19.0.1 --subnet 172.19.0.0/16 backend_mqtt
docker volume create --driver local --name camera_videos
docker plugin install grafana/loki-docker-driver:arm-v7 --alias loki --grant-all-permissions

# Disable DHCP for virtual interfaces (created by docker)
# without this line, the raspberry pi crashes after 5-10 seconds on WiFi.
# Sources: https://www.raspberrypi.org/forums/viewtopic.php?t=282425#p1712939
# https://github.com/docker/compose/issues/7051

grep -q "denyinterfaces veth*" /etc/dhcpcd.conf
if [ $? -eq 1 ]; then
  echo "denyinterfaces veth*" >> /etc/dhcpcd.conf
fi
