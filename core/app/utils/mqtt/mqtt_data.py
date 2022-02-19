from dataclasses import dataclass
from typing import Callable, List, Optional, Union
import datetime
import json
import struct
from distutils.util import strtobool

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
class MqttAuth:
    username: str
    password: str

@dataclass
class MqttOneShootConfig:
    hostname: str
    port: int
    auth: MqttAuth

@dataclass
class MQTTSendMessage:
    topic: str
    payload: Optional[str] = None
    qos: int = 1
    retain: bool = False

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
    def callback(self, message: MqttMessage) -> None:
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
    Either a byte representation (0x00 or 0x01)
    or any boolean string representation (https://docs.python.org/3/distutils/apiref.html#distutils.util.strtobool)

    Warning: hacky things... have to try strtobool before because unpack with b'0' gives True!
    """
    def callback(self, message: MqttMessage):
        if isinstance(message.payload, bytes):
            str_payload = message.payload.decode('utf-8')
        else:
            str_payload = message.payload

        try:
            payload = strtobool(str_payload) == 1
        except ValueError:
            pass
        else:
            message.payload = payload
            return super().callback(message)

        try:
            decoded = struct.unpack('?', message.payload)
        except (struct.error, TypeError):
            pass
        else:
            payload = decoded[0]
            message.payload = payload
            return super().callback(message)

        return self._log_error(message)

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
