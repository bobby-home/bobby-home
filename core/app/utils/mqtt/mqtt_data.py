from dataclasses import dataclass
from typing import Callable, List, Optional, Union
import datetime
import json
import struct

from hello_django.loggers import LOGGER

PublishPayloadType = Union[str, bytes, int, float, dict, None]


@dataclass
class MqttConfig:
    hostname: str
    port: int

    client_id: str = None
    clean_session: bool = False

    keepalive: int = 120
    user: str = None
    password: str = None


@dataclass
class MqttMessage:
    topic: str
    payload: PublishPayloadType
    qos: int
    retain: bool
    subscribed_topic: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None


MessageCallbackType = Callable[[MqttMessage], None]


@dataclass
class Subscription:
    topic: str


@dataclass
class MqttTopicSubscription(Subscription):
    _callback: MessageCallbackType
    qos: int = 1

    @staticmethod
    def _log_error(message: MqttMessage) -> None:
        # TODO: see #102
        LOGGER.critical(
            f"Can't perform payload transform: on {message}"
        )

    def callback(self, message: MqttMessage) -> None:
        self._callback(message)


@dataclass
class MqttTopicFilterSubscription(Subscription):
    """
    Sometimes, we don't want to attach a callback to a subscribe.
    The goal is to set the qos for a "scope".
    For example, I may want the qos to be equals to 2 for the topic "motion/#"
    and then add callbacks for motion/camera, motion/picture, ...
    -> this is done by adding MqttTopicSubscription in the "topics" list.
    """
    topics: List[MqttTopicSubscription]
    qos: int = 1


@dataclass
class MqttTopicSubscriptionJson(MqttTopicSubscription):
    def callback(self, message: MqttMessage):
        try:
            payload = json.loads(message.payload)
        except json.JSONDecodeError:
            return self._log_error(message)

        message.payload = payload
        super().callback(message)


@dataclass
class MqttTopicSubscriptionBoolean(MqttTopicSubscription):
    """
    Handle boolean mqtt payload: "decode" it and convert it to Python boolean.
    """
    def callback(self, message: MqttMessage):
        try:
            decoded = struct.unpack('?', message.payload)
        except (struct.error, TypeError):
            return self._log_error(message)

        payload = decoded[0]
        message.payload = payload
        super().callback(message)


@dataclass
class MqttTopicSubscriptionEncoding(MqttTopicSubscription):
    encoding: str = "utf-8"

    def callback(self, message: MqttMessage):
        try:
            payload = message.payload.decode(self.encoding)
        except (AttributeError, UnicodeDecodeError):
            return self._log_error(message)

        message.payload = payload
        super().callback(message)
