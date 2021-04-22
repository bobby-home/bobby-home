#!/bin/bash

# bash deploy.sh pi@mx_rpi /home/pi/core <env?>

RSYNC="$1:$2"

FILES="../setup-ssh-keys.sh ./docker-compose.yml ./docker-compose.prod.yml ./Makefile config"

if [ -n "$3" ]; then
    FILES="$FILES ./.env"
fi

echo "Deploy core $FILES to $RSYNC"

rsync --exclude=passwd -avt $FILES "$RSYNC"

