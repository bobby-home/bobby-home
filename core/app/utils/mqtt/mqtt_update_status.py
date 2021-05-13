from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence, Type, TypeVar
from utils.mqtt import MQTT
from utils.mqtt.mqtt_data import MqttMessage, MqttTopicSubscriptionJson
from distutils.util import strtobool
import re


@dataclass
class TopicMatcher:
    _topic_matcher: str


T = TypeVar('T')


def topic_regex(topic: str, t: T) -> T:
    match = re.match(t._topic_matcher, topic)

    if match:
        groups = match.groupdict()
        return t(**groups) # type: ignore

    raise ValueError(f'topic {topic} wrong format. {t._topic_matcher}')

class OnUpdateStatusHandler(ABC):
 
    @abstractmethod
    def on_update_device(self, payload, device_id: str) -> None:
        pass

    @abstractmethod
    def on_update_all(self, payload) -> None:
        pass


@dataclass
class UpdateStatusTopic:
    service: str
    device_id: Optional[str] = None

    _topic_matcher: str = r"^update\/(?P<service>[\w]+)(?:\/(?P<device_id>[\w]+)?)?"


class OnUpdate:
    def __init__(self, handler: OnUpdateStatusHandler, payload: Type[Any]) -> None:
        self._handler = handler
        self._payload_type = payload

    def on_update(self, message: MqttMessage) -> None:
        topic = topic_regex(message.topic, UpdateStatusTopic)
        data_payload = self._payload_type(**message.payload)

        if topic.device_id is not None:
            self._handler.on_update_device(data_payload, topic.device_id)
        else:
            self._handler.on_update_all(data_payload)


@dataclass
class UpdateStatusDescriptor:
    name: str
    on_update: Type[OnUpdateStatusHandler]
    payload_type: Type[Any]


def bind_on_update(service_name: str, handler_instance: OnUpdateStatusHandler, payload_type) -> MqttTopicSubscriptionJson:
    on_update = OnUpdate(handler_instance, payload_type)

    return MqttTopicSubscriptionJson(f'update/{service_name}/+', on_update.on_update)


def on_updates(mqtt: MQTT, services: Sequence[UpdateStatusDescriptor]) -> None:
    subscriptions = [bind_on_update(service.name, service.on_update(), service.payload_type) for service in services]
    mqtt.add_subscribe(subscriptions) 
 
