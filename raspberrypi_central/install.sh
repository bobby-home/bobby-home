#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git vim libffi-dev libssl-dev python python-pip python3-pip

# Docker
sudo apt-get remove python-configparser
sudo apt-get -y install python3-pip
sudo pip3 install docker-compose

curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi

# enable the pi camera.
sudo raspi-config nonint do_camera 0
