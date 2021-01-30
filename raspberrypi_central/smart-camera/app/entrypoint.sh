ping -c 1 "$MQTT_HOSTNAME"
echo "Waiting for mqtt broker $MQTT_HOSTNAME:$MQTT_PORT"
while ! nc -z "$MQTT_HOSTNAME" "$MQTT_PORT"; do
  sleep 0.1
done
echo "MQTT broker started"
