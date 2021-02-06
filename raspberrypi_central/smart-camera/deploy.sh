#!/bin/bash

# bash deploy.sh pi@mx_rpi:/home/pi/mx-tech-house/smart-camera-prod

echo "Deploy to" $@

rsync -avt ./docker-compose.yml ./docker-compose.prod.yml ./Makefile ./.env $@
