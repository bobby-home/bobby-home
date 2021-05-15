import dataclasses
from typing import Any, Dict
import json
import uuid
from typing import Any, Optional, Sequence
from django.utils import timezone
from automation.models import ActionMqttPublish
from paho.mqtt.publish import single
import paho.mqtt.client as mqtt


def _payload_str_format(payload: Dict[Any, Any], data: Dict[Any, Any]) -> Dict[Any, Any]:
    r = {}

    for key, value in payload.items():
        if isinstance(value, str) and '{' in value:
            r[key] = value.format(**data)
        else:
            r[key] = value

    return r


def mqtt_publish(actions: Sequence[ActionMqttPublish], data: Optional[Any] = None) -> None:
    for action in actions:
        mqtt_client = action.mqtt_client

        topic = action.topic
        payload = action.payload_json

        if data and dataclasses.is_dataclass(data):
            d = dataclasses.asdict(data)
            topic = topic.format(**d)
            if action.payload_json:
                payload = _payload_str_format(json.loads(action.payload_json), d)

        single(
            topic,
            payload=json.dumps(payload),
            qos=action.qos,
            retain=action.retain,
            hostname=mqtt_client.host,
            port=mqtt_client.port,
            protocol=mqtt.MQTTv311,
            transport="tcp",
            auth={"username": mqtt_client.username, "password": mqtt_client.password},
            client_id=f"automation-{str(uuid.uuid4())}"
        )

        action.last_run_datetime = timezone.now()
        action.save()
