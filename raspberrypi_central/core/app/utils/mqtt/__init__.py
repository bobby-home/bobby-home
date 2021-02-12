import os
from functools import partial
from typing import List
import logging
import utils.date as dt_utils
from utils.mqtt.mqtt_data import MqttConfig, Subscription, MqttTopicSubscription, MqttTopicFilterSubscription, MqttMessage
import paho.mqtt.client as mqtt


_LOGGER = logging.getLogger(__name__)


class MQTT:
    """
    Wrapper around Paho MQTT.
    This enables us to wrap mqtt message to its own class to group data in a clean manner.
    """
    def __init__(self, config: MqttConfig, mqtt_client_constructor):
        self._config = config
        self._mqtt_client_constructor = mqtt_client_constructor
        self.client = self._init_mqtt_client()

    def _init_mqtt_client(self) -> mqtt.Client:
        config = self._config
        client: mqtt.Client = self._mqtt_client_constructor(client_id=config.client_id, protocol=mqtt.MQTTv5)

        if config.user is not None and config.password is not None:
            client.username_pw_set(config.user, config.password)

        client.connect(config.hostname, int(config.port), keepalive=config.keepalive)

        client.on_connect = self._mqtt_on_connect

        # TODO: what do we do when disconnect happens? It is very bad!
        # client.on_disconnect = self._mqtt_on_disconnect

        return client

    def _mqtt_on_connect(self, _idk, _mqttc, _userdata, _flags, result_code: int):
        # pylint: disable=import-outside-toplevel
        import paho.mqtt.client as mqtt

        if result_code != mqtt.CONNACK_ACCEPTED:
            _LOGGER.error(
                "Unable to connect to the MQTT broker: %s",
                mqtt.connack_string(result_code),
            )
            return

    @staticmethod
    def _wrap_subscription_callback(subscription: MqttTopicSubscription):
        return partial(MQTT._mqtt_on_message_wrapper, subscription)

    def add_subscribe(self, subscriptions: List[Subscription]):

        def _mqtt_add_callback(subscription: MqttTopicSubscription):
            subscription_callback = self._wrap_subscription_callback(subscription)
            self.client.message_callback_add(subscription.topic, subscription_callback)

        for subscription in subscriptions:
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
            self.client.subscribe(subscription.topic, subscription.qos)

            if isinstance(subscription, MqttTopicFilterSubscription):
                for sub in subscription.topics:
                    _mqtt_add_callback(sub)
            else:
                _mqtt_add_callback(subscription)

    @staticmethod
    def _mqtt_on_message_wrapper(subscription: MqttTopicSubscription, _mqttc, _userdata, msg):
        timestamp = dt_utils.utcnow()

        subscription.callback(MqttMessage(
            msg.topic,
            msg.payload,
            msg.qos,
            msg.retain,
            subscription.topic,
            timestamp,
        ))

    def publish(self, topic, message, qos=1, retain=False):
        self.client.publish(topic, message, qos=qos, retain=retain)


def mqtt_factory(client_id: str = None, clean_session=False) -> MQTT:
    if client_id is None:
        clean_session = True

    mqttConfig = MqttConfig(
        client_id=client_id,
        clean_session=clean_session,
        user=os.environ['MQTT_USER'],
        password=os.environ['MQTT_PASSWORD'],
        hostname=os.environ['MQTT_HOSTNAME'],
        port=int(os.environ['MQTT_PORT'])
    )

    return MQTT(mqttConfig, mqtt.Client)
