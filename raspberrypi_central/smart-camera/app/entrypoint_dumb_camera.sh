#!/bin/bash

# export all env variables in .env file and then run the camera_frame_producer.py
# thanks to this, we avoid to add a python dependency to parse the file.
# it's natively done by shell.

export MEDIA_FOLDER=/var/lib/camera/media
set -a; source ../.env; source ~/.device; set +a && python3 -m pip install --user --requirement ./requirements.txt && python3 dumb_camera.py
