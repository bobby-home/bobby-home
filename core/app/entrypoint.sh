#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
  ping -c 1 "$SQL_HOST"
  echo "Waiting for postgres $SQL_HOST:$SQL_PORT"
  while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
    sleep 0.1
  done
  echo "PostgreSQL started"
fi

echo "Waiting for RabbitMQ $RABBIT_HOSTNAME:$RABBIT_PORT"
ping -c 1 "$RABBIT_HOSTNAME"
while ! nc -z "$RABBIT_HOSTNAME" "$RABBIT_PORT"; do
  sleep 0.1
done
echo "RabbitMQ started"

ping -c 1 "$MQTT_HOSTNAME"
echo "Waiting for mqtt $MQTT_HOSTNAME:$MQTT_PORT"
while ! nc -z "$MQTT_HOSTNAME" "$MQTT_PORT"; do
  sleep 0.1
done
echo "MQTT started"

# don't migrate here because multiple containers use the same image and the same entrypoint:
# concurrent migrate that produces a lot of database errors.
# just run migrate for web container, with command...
# it's maybe a temp solution until I use 1 image per container.
#python manage.py migrate --no-input

exec "$@"
