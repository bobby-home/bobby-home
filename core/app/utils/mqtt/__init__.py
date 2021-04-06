import os
from functools import partial
from typing import List, Callable
import logging
import utils.date as dt_utils
from paho.mqtt.reasoncodes import ReasonCodes
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
        self.on_connected_callbacks: List[Callable[[MQTT], None]] = []
        self.client = self._init_mqtt_client()

    def _init_mqtt_client(self) -> mqtt.Client:
        config = self._config
        client: mqtt.Client = self._mqtt_client_constructor(client_id=config.client_id, protocol=mqtt.MQTTv5)

        if config.user is not None and config.password is not None:
            client.username_pw_set(config.user, config.password)

        client.connect(config.hostname, int(config.port), keepalive=config.keepalive)

        client.on_connect = self._mqtt_on_connect

        # TODO: what do we do when disconnect happens? It is very bad!
        client.on_disconnect = self._mqtt_on_disconnect

        return client

    @staticmethod
    def _mqtt_on_disconnect(_client, _userdata, rc):
        print(f'_mqtt_on_disconnect reason code: {mqtt.connack_string(rc)}')

    def _mqtt_on_connect(self, _client, _userdata, _flags, rc: ReasonCodes, _properties):
        # print(_client._protocol)
        print(f'_mqtt_on_connect rc: {rc}')

        if rc != mqtt.CONNACK_ACCEPTED:
            _LOGGER.error(
                "Unable to connect to the MQTT broker: %s",
                mqtt.connack_string(rc),
            )
            return

        for callback in self.on_connected_callbacks:
            callback(self)

    @staticmethod
    def _wrap_subscription_callback(subscription: MqttTopicSubscription):
        return partial(MQTT._mqtt_on_message_wrapper, subscription)

    def add_subscribe(self, subscriptions: List[Subscription]):

        def _mqtt_add_callback(sub: MqttTopicSubscription):
            subscription_callback = self._wrap_subscription_callback(sub)
            self.client.message_callback_add(sub.topic, subscription_callback)

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
    def _mqtt_on_message_wrapper(subscription: MqttTopicSubscription, _mqttc, _userdata, msg: mqtt.MQTTMessage) -> None:
        """Callback given to Paho mqtt which calls it when it receives a mqtt message. Then it calls `subscription.callback` with computed `MqttMessage`.
        Used to extract data given by Paho mqtt and to call our `subscription.callback`.
        Thanks to this, our system is not concerned by the library.

        Parameters
        ----------
        subscription : MqttTopicSubscription
            The
        _mqttc
            Paho mqtt client.
        _userdata
            Paho mqtt user data.
        msg : mqtt.MQTTMessage
            MQTTMessage object given by Paho mqtt.

        Returns
        -------
        None
        """
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
        # otherwise it will raise Exception and crash.
        if qos is None:
            qos = 1

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
