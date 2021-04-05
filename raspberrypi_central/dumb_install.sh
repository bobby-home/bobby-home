#!/bin/bash

# Script used to setup raspberry pi zero for dumb camera.
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip

# enable the pi camera. Warning: need reboot (done at the end).
sudo raspi-config nonint do_camera 0

# folder used to store videos.
sudo mkdir -p /var/lib/camera/media && sudo chown -R pi:pi /var/lib/camera/media

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

sudo reboot
