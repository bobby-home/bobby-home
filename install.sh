#!/bin/zsh
sudo apt update && sudo apt upgrade -y
sudo apt install -y git vim libffi-dev libssl-dev python python-pip python3-pip ipcalc nmap

# Docker
sudo apt-get remove -y python-configparser
sudo apt-get -y install python3-pip
sudo pip3 install docker-compose

sudo apt autoremove

curl -sSL https://get.docker.com | sh

# enable the pi camera. Warning: need reboot (done at the end).
sudo raspi-config nonint do_camera 0

sudo docker network create --gateway 172.80.0.1 --subnet 172.80.0.0/16 backend_mqtt
sudo docker volume create --driver local --name camera_videos
sudo docker plugin install grafana/loki-docker-driver:arm-v7 --alias loki --grant-all-permissions

# Disable DHCP for virtual interfaces (created by docker)
# without this line, the raspberry pi crashes after 5-10 seconds on WiFi.
# Sources: https://www.raspberrypi.org/forums/viewtopic.php?t=282425#p1712939
# https://github.com/docker/compose/issues/7051

grep -q "denyinterfaces veth*" /etc/dhcpcd.conf
if [ $? -eq 1 ]; then
  echo "denyinterfaces veth*" >> /etc/dhcpcd.conf
fi

touch ~/.device

grep -q "DEVICE_ID=" ~/.device
if [ $? -eq 1 ]; then
  DEVICE_ID=$(cat /proc/sys/kernel/random/uuid | cut -d "-" -f 1)
  echo "DEVICE_ID=$DEVICE_ID" >> ~/.device && source ~/.device
fi

grep -q "DEVICE_MODEL=" ~/.device
if [ $? -eq 1 ]; then
  # xargs is used to trim string
  DEVICE_MODEL=$(cat /proc/device-tree/model | awk -F 'Rev' '{print $1}' | xargs)
  echo "DEVICE_MODEL=\"$DEVICE_MODEL\"" >> ~/.device && source ~/.device
fi

source ~/.device

grep -q "$DEVICE_ID" /etc/hosts
if [ $? -eq 1 ]; then
  # Change hostname "raspberrypi" to the device id, so it's easier to find the device on the network.
  CURRENT_HOSTNAME="raspberrypi"
  NEW_HOSTNAME=$DEVICE_ID

  sudo hostnamectl set-hostname "$NEW_HOSTNAME"
  sudo sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t$NEW_HOSTNAME/g" /etc/hosts
fi

sudo usermod -aG docker pi
sudo reboot
