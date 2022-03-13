import os
import logging
import json
from unittest import TestCase
from uuid import uuid4
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class ObjectDetectionTestCase(TestCase):
    def setUp(self) -> None:
        catPicture = open('./pictures/cat1.jpg', 'rb')
        self.catBinary = catPicture.read(-1)
        catPicture.close()

        self.event_ref = str(uuid4())
        self.publish_topic = f'object-detection/picture/{self.event_ref}'
        self.answer_topic = f'object-detection/response/{self.event_ref}'

        user = os.environ['MQTT_USER']
        password = os.environ['MQTT_PASSWORD']
        self.hostname = os.environ['MQTT_HOSTNAME']
        self.port = int(os.environ['MQTT_PORT'])

        self.client = mqtt.Client(client_id="test_object_detection_frame")
        self.client.username_pw_set(user, password)
        self.client.connect(self.hostname, self.port)

    def on_anwser(self, _client, _userdata, msg) -> None:
        payload = json.loads(msg.payload)
        LOGGER.info(f'on answer payload={payload}')

        self.assertIn('event_ref', payload)
        self.assertIn('detections', payload)
        detections = payload['detections']

        self.assertEqual(payload['event_ref'], self.event_ref)
        self.assertGreaterEqual(len(detections), 1, "Must have at least one detection")

        # assume the cat is the first detection.
        cat_detection = detections[0]
        self.assertEqual(cat_detection['class_id'], 'cat', "Must be a cat")

        self.client.disconnect()

    def test_detection(self) -> None:
        LOGGER.info(f'subscribe to {self.answer_topic}')
        self.client.subscribe(self.answer_topic)
        self.client.message_callback_add(self.answer_topic, self.on_anwser)

        LOGGER.info(f'publish picture to {self.publish_topic}')
        self.client.publish(self.publish_topic, self.catBinary)
        self.client.loop_forever()

