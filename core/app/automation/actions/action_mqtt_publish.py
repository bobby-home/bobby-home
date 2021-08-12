import dataclasses
import struct
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


def _get_payload(action: ActionMqttPublish, data: Optional[Dict]) -> Any:
    payload = action.payload_json

    if payload:
        if isinstance(payload, str):
            payload = json.loads(payload)

        if data:
            payload = _payload_str_format(payload, data)

        return json.dumps(payload)

    payload = action.payload_boolean
    if payload is not None:
        return struct.pack('?', payload)
        
    raise ValueError(f'action {action} does not contains any supported payload.')

def mqtt_publish(actions: Sequence[ActionMqttPublish], data: Optional[Any] = None) -> None:
    data_parsed = None
    if data and dataclasses.is_dataclass(data):
        data_parsed = dataclasses.asdict(data)
    
    for action in actions:
        mqtt_client = action.mqtt_client
        topic = action.topic
        payload = _get_payload(action, data_parsed)

        if data_parsed:
            topic = topic.format(**data_parsed)
        
        single(
            topic,
            payload=payload,
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
