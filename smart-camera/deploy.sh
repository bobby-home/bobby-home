#!/bin/bash

# bash deploy.sh pi@mx_rpi /home/pi/camera <dumb?>

RSYNC="$1:$2"

if [ -n "$3" ]; then
    echo "Deploy dumb camera to $RSYNC"
  # dumb deploy: it does not use docker, so deploy the whole app.
  rsync --exclude-from='sync_exclude' -avt --delete . "$RSYNC"
  ssh "$1" chmod +x $2/app/entrypoint_dumb_camera.sh
  ssh "$1" sudo cp $2/dumb_camera.service /etc/systemd/system/dumb_camera.service
  ssh "$1" sudo systemctl enable dumb_camera.service
else
  echo "Deploy smart camera to $RSYNC"
  rsync --exclude-from='sync_exclude' -avt --delete ./docker-compose.yml ./docker-compose.prod.yml ./Makefile ./.env "$RSYNC"
fi
