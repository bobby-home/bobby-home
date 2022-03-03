#!/bin/bash

echo "MQTT_SERVER is $MQTT_SERVER"

IP=''
PORT=''

# first part could be a docker service name (mqtt_broker), or an IP.
if [[ $MQTT_SERVER =~ tcp://(.+):([0-9]+) ]]; then
    IP=${BASH_REMATCH[1]}
    PORT=${BASH_REMATCH[2]}
else
    echo "can't extract the ip:port from $MQTT_SERVER" >&2
    exit 1
fi

echo "Waiting for mqtt broker $IP:$PORT"
while ! nc -z "$IP" "$PORT"; do
  sleep 0.1
done
echo "MQTT broker started"

# run command with exec to pass control
echo "Running CMD: $@"
exec "$@"
