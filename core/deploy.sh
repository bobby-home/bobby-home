#!/bin/bash

# bash deploy.sh pi@mx_rpi /home/pi/core

RSYNC="$1:$2"

echo "Deploy core to $RSYNC"

rsync --exclude=passwd -avt ../setup-ssh-keys.sh ./docker-compose.yml ./docker-compose.prod.yml ./Makefile ./.env up.sh config "$RSYNC"
