#!/bin/bash

sudo apt install -y vim libffi-dev libssl-dev python python-pip python3-pip pipenv

# Docker
sudo apt-get remove python-configparser
sudo apt-get install python3-pip
sudo pip3 install docker-compose
