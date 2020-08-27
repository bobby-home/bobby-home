#!/bin/bash

sudo apt install -y ipcalc nmap git vim libffi-dev libssl-dev python python-pip python3-pip pipenv

# Docker
sudo apt-get remove python-configparser
sudo apt-get -y install python3-pip
sudo pip3 install docker-compose
