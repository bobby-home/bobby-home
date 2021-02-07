#!/bin/bash

# Script used to setup raspberry pi zero.

sudo apt install git
pip3 install --user --requirement ./requirements.txt

sudo mkdir -p /var/lib/camera/media && sudo chown -R pi:pi /var/lib/camera/media
