#!/bin/bash

# send docker-compose.prod.yml, docker-compose.yml, config folder, .env, Makefile, up.sh

echo "Deploy to" $@

rsync -avt ./docker-compose.yml ./docker-compose.prod.yml ./Makefile ./.env up.sh config $@
