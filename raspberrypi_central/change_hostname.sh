#!/bin/bash

CURRENT_HOSTNAME=$1
NEW_HOSTNAME=$2

sudo hostnamectl set-hostname $NEW_HOSTNAME
sudo sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t$NEW_HOSTNAME/g" /etc/hosts
sudo reboot
