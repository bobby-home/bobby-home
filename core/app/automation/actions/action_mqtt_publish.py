import json
import uuid
from typing import Sequence
from django.utils import timezone
from automation.models import ActionMqttPublish
from paho.mqtt.publish import single
import paho.mqtt.client as mqtt


def mqtt_publish(actions: Sequence[ActionMqttPublish]) -> None:
    for action in actions:
        mqtt_client = action.mqtt_client

        single(
            action.topic,
            payload=json.dumps(action.payload_json),
            qos=action.qos,
            retain=action.retain,
            hostname=mqtt_client.host,
            port=mqtt_client.port,
            protocol=mqtt.MQTTv5,
            transport="tcp",
            auth={"username": mqtt_client.username, "password": mqtt_client.password},
            client_id=f"automation-{str(uuid.uuid4())}"
        )

        action.last_run_datetime = timezone.now()
        action.save()
