import unittest

from utils.mqtt import MQTT, MqttConfig
from unittest.mock import Mock, call

from utils.mqtt.mqtt_data import MqttTopicSubscriptionBoolean, MqttTopicFilterSubscription, MqttTopicSubscriptionJson, \
    MqttTopicSubscription


class MqttTestCase(unittest.TestCase):
    def setUp(self) -> None:
        mqttConfig = MqttConfig(
            client_id='random_id_here',
            clean_session=True,
            user='mx',
            password='some_password',
            hostname='some_hostname',
            port=1883
        )

        self.mqtt_client = Mock()
        self.mqtt_client_factory = lambda *args, **kwargs: self.mqtt_client

        self.mqtt = MQTT(mqttConfig, self.mqtt_client_factory)

    def test_add_subscribe_filter(self):
        on_connected = [Mock(), Mock()]

        subscriber = MqttTopicFilterSubscription(
            topic='motion/#',
            qos=1,
            topics=[
                MqttTopicSubscriptionJson('motion/camera/+', on_connected[0]),
                MqttTopicSubscription('motion/picture/+/+/+', on_connected[0]),
            ],
        )
        self.mqtt._wrap_subscription_callback = lambda sub: sub

        self.mqtt.add_subscribe([subscriber])

        subscribe_calls = [
            call(subscriber.topic, subscriber.qos)
        ]

        callback_add_calls = []
        wrap_subscription_callback_calls = []

        for i, sub in enumerate(subscriber.topics):
            callback_add_calls.append(
                call(sub.topic, subscriber.topics[i])
            )

            wrap_subscription_callback_calls.append(call(subscriber))

        self.mqtt_client.subscribe.assert_has_calls(subscribe_calls)
        self.mqtt_client.message_callback_add.assert_has_calls(callback_add_calls)


    def test_add_subscribe(self):
        on_connected = [Mock(), Mock()]

        subscribers = [
            MqttTopicSubscriptionBoolean('connected/some_service/+', on_connected[0]),
            MqttTopicSubscriptionBoolean('connected/some_other_service/+', on_connected[1])
        ]

        self.mqtt._wrap_subscription_callback = lambda sub: sub

        self.mqtt.add_subscribe(subscribers)

        subscribe_calls = []
        callback_add_calls = []

        for i, subscriber in enumerate(subscribers):
            subscribe_calls.append(
                call(subscriber.topic, subscriber.qos)
            )

            callback_add_calls.append(
                call(subscriber.topic, subscribers[i])
            )


        self.mqtt_client.subscribe.assert_has_calls(subscribe_calls)
        self.mqtt_client.message_callback_add.assert_has_calls(callback_add_calls)
