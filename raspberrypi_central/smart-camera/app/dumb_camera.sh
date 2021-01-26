#!/bin/bash

# export all env variables in .env file and then run the dumb_camera.py
# thanks to this, we avoid to add a python dependency to parse the file.
# it's natively done by shell.
set -a; source ../.env; set +a && python3 dumb_camera.py
