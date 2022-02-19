import json
from typing import Callable
from unittest import TestCase
from utils.mqtt.mqtt_data import MQTTSendMessage, MqttTopicFilterSubscription, MqttTopicSubscriptionJson
from utils.mqtt import MQTTOneShoot, mqtt_factory, mqtt_one_shoot_factory


class MQTTOneShootIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.topic = 'testing/json'
        self.str_json_payloads = []
        self.json_payloads = []
        self.messages = []
        self.received = 0

        for i in range(2):
            strp = '{"hello": "world", "things": {"answer": "42", "number": '+str(i)+'}}'
            self.str_json_payloads.append(strp)
            self.json_payloads.append(json.loads(strp))
            self.messages.append(MQTTSendMessage(topic=self.topic, payload=strp))

        self.mqtt_client_os: MQTTOneShoot = mqtt_one_shoot_factory()
        self.mqtt_client = mqtt_factory()
        return super().setUp()

    def on_message_json_cb(self, _client, _userdata, msg):
        self.assertEqual(msg.payload, str.encode(self.str_json_payloads[0]))
        self.mqtt_client.client.disconnect()

    def on_messages_json_cb(self, _client, _userdata, msg):
        i = self.received

        self.assertEqual(msg.payload, str.encode(self.str_json_payloads[i]))
        self.received = self.received+1

        if i == len(self.messages) -1:
            self.mqtt_client.client.disconnect()

    def test_publish_single(self):
        self.mqtt_client.client.on_message = self.on_message_json_cb
        self.mqtt_client.client.subscribe(self.topic)
        self.mqtt_client_os.single(self.messages[0], 'testing_uuid')
        self.mqtt_client.client.loop_forever()

    def test_publish_multiple(self):
        self.mqtt_client.client.on_message = self.on_messages_json_cb
        self.mqtt_client.client.subscribe(self.topic)
        self.mqtt_client_os.multiple(self.messages, 'testing_uuid_multiple')
        self.mqtt_client.client.loop_forever()


class MQTTIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.str_json_payload = '{"hello": "world", "things": {"answer": "42"}}'
        self.json_payload = json.loads(self.str_json_payload)
        self.mqtt_client = mqtt_factory()
        return super().setUp()

    def on_message_json_cb(self, message: MQTTSendMessage):
        self.assertDictEqual(message.payload, self.json_payload)
        self.mqtt_client.client.disconnect()

    def raw_publish_json(self):
        self.mqtt_client.client.publish('testing/json', self.str_json_payload)

    def add_json_subscribe(self, cb: Callable):
        self.mqtt_client.add_subscribe((
            MqttTopicFilterSubscription(
                topic='testing/#',
                qos=1,
                topics=[
                    MqttTopicSubscriptionJson('testing/json', cb),
                ],
            ),
        ))

    def test_publish_json(self):
        self.add_json_subscribe(self.on_message_json_cb)
        self.raw_publish_json()
        self.mqtt_client.client.loop_forever()
