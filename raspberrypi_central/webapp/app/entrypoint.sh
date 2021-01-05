#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres $SQL_HOST:$SQL_PORT"
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

echo "Waiting for RabbitMQ $RABBIT_HOSTNAME:$RABBIT_PORT"
while ! nc -z $RABBIT_HOSTNAME $RABBIT_PORT; do
  sleep 0.1
done
echo "RabbitMQ started"

echo "Waiting for mqtt $MQTT_HOSTNAME:$MQTT_PORT"
while ! nc -z $MQTT_HOSTNAME $MQTT_PORT; do
  sleep 0.1
done
echo "MQTT started"

# pipenv run python manage.py flush --no-input
# pipenv run python manage.py migrate --no-input

exec "$@"
