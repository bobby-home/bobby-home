import os
import datetime
from functools import partial
from typing import Callable, List, Optional, Union
import logging
import json
from dataclasses import dataclass
import utils.date as dt_utils
import struct


_LOGGER = logging.getLogger(__name__)

PublishPayloadType = Union[str, bytes, int, float, None]


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
    encoding: str = "utf-8"
    qos: int = 1

    def callback(self, message: MqttMessage):
        self._callback(message)


@dataclass
class MqttTopicSubscriptionJson(MqttTopicSubscription):
    def callback(self, message: MqttMessage):
        try:
            payload = json.loads(message.payload)
            message.payload = payload
            super().callback(message)
        except json.JSONDecodeError:
            _LOGGER.error(
                f"Unable to decode json payload {message.payload} {message}"
            )


@dataclass
class MqttTopicSubscriptionBoolean(MqttTopicSubscription):
    def callback(self, message: MqttMessage):
        try:
            decoded = struct.unpack('?', 'lol')
        except (struct.error, TypeError):
            print('error')
            return

        payload = decoded[0]
        print(payload)
        message.payload = payload
        super().callback(message)


@dataclass
class MqttTopicFilterSubscription(Subscription):
    """
    Sometimes, we don't want to attach a callback to a subscribe.
    The goal is to set the qos for a "scope".
    For example, I may want the qos to be equals to 2 for the topic "motion/#"
    and then add callbacks for motion/camera, motion/picture, ...
    -> this is done by adding MqttTopicSubscription in the "topics" list.
    """
    topic: str
    topics: List[MqttTopicSubscription]
    qos: int = 1


@dataclass
class MqttConfig:
    hostname: str
    port: int

    client_id: str = None
    clean_session: bool = False

    keepalive: int = 120
    user: str = None
    password: str = None


class MQTT():
    def __init__(self, config: MqttConfig):
        self._config = config
        self._init_mqtt_client()

    def _init_mqtt_client(self):
        config = self._config
        # We don't import on the top because some integrations
        # should be able to optionally rely on MQTT.
        # pylint: disable=import-outside-toplevel
        import paho.mqtt.client as mqtt

        client = mqtt.Client(client_id=config.client_id, clean_session=config.clean_session)

        if config.user is not None and config.password is not None:
            client.username_pw_set(config.user, config.password)

        client.connect(config.hostname, int(config.port), keepalive=config.keepalive)

        client.on_connect = self._mqtt_on_connect

        # TODO: what do we do when disconnect happens? It is very bad!
        # client.on_disconnect = self._mqtt_on_disconnect

        self._client = client

    def _mqtt_on_connect(self, _mqttc, _userdata, _flags, result_code: int):
        # pylint: disable=import-outside-toplevel
        import paho.mqtt.client as mqtt

        if result_code != mqtt.CONNACK_ACCEPTED:
            _LOGGER.error(
                "Unable to connect to the MQTT broker: %s",
                mqtt.connack_string(result_code),
            )
            return

    def add_subscribe(self, subscriptions: List[Subscription]):
        for subscription in subscriptions:

            def _mqtt_addCallback(subscription: MqttTopicSubscription):
                subscription_callback = partial(self._mqtt_on_message_wrapper, subscription)
                self._client.message_callback_add(subscription.topic, subscription_callback)

            """
            Subscribe strategy:
            - use paho mqtt .subscribe() with .add_callback
            Why? Avoid the huge function that receives all messages for all messages and dispatch it.
            -> paho mqtt can do it for us, so we don't have to keep in memory all the topic/handler do dispatch topic -> handler.

            From the documentation:
            "This function allows you to define callbacks that handle incoming messages for specific subscription filters,
            including with wildcards. This lets you, for example, subscribe to sensors/#
            and have one callback to handle sensors/temperature and another to handle sensors/humidity."

            We also use it for single topic/handler, for example: "/something/else" -> subscribe -> addCallbackHandler.
            """
            self._client.subscribe(subscription.topic, subscription.qos)

            if isinstance(subscription, MqttTopicFilterSubscription):
                for sub in subscription.topics:
                    _mqtt_addCallback(sub)
            else:
                _mqtt_addCallback(sub)

    def _mqtt_on_message_wrapper(self, subscription: MqttTopicSubscription, _mqttc, _userdata, msg):
        timestamp = dt_utils.utcnow()

        payload = msg.payload

        if subscription.encoding is not None:
            try:
                pass
                # payload = msg.payload.decode(subscription.encoding)
            except (AttributeError, UnicodeDecodeError):
                """
                If we cannot decode a payload we don't call the callback
                because this can lead to errors.
                """
                _LOGGER.warning(
                    "Can't decode payload %s on %s with encoding %s (for %s)",
                    msg.payload,
                    msg.topic,
                    subscription.encoding,
                    subscription.callback,
                )
                return

        subscription.callback(MqttMessage(
            msg.topic,
            payload,
            msg.qos,
            msg.retain,
            subscription.topic,
            timestamp,
        ))

    def publish(self, topic, message, qos=None, retain=False):
        self._client.publish(topic, message, qos=qos, retain=retain)


def mqtt_factory(client_id: str = None, clean_session=False) -> MQTT:
    if client_id is not None:
        clean_session = True

    mqttConfig = MqttConfig(
        client_id=client_id,
        clean_session=clean_session,
        user=os.environ['MQTT_USER'],
        password=os.environ['MQTT_PASSWORD'],
        hostname=os.environ['MQTT_HOSTNAME'],
        port=os.environ['MQTT_PORT']
    )

    return MQTT(mqttConfig)
