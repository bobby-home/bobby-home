"""
Don't judge me, the code is horrible.
I want to handle async things with sync code, so it's just garbage.
The most important: it works, I'll rewrite this in the future.
"""
import os
import logging
import json
import time
from unittest import TestCase
from uuid import uuid4
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class FunctionalTestCase(TestCase):
    def setUp(self) -> None:
        catPicture = open("./pictures/cat2.jpg", "rb")
        self.catBinary = catPicture.read(-1)
        catPicture.close()

        peoplePicture = open("./pictures/people-1.jpg", "rb")
        self.peopleBinary = peoplePicture.read(-1)
        peoplePicture.close()

        uuid = str(uuid4())
        self.deviceId = uuid.split('-')[-1]

        self.publishTopic = f'ia/picture/{self.deviceId}'

        user = os.environ['MQTT_USER']
        password = os.environ['MQTT_PASSWORD']
        self.hostname = os.environ['MQTT_HOSTNAME']
        self.port = int(os.environ['MQTT_PORT'])
        self.up_threshold = int(os.environ['NB_FRAME_UP_THRESHOLD'])
        self.down_threshold = int(os.environ['NB_FRAME_DOWN_THRESHOLD'])

        self.client = mqtt.Client(client_id="test_object_detection")
        self.client.username_pw_set(user, password)
        self.client.connect(self.hostname, self.port)

        self.expect_motion = True
        self.should_on_motion_triggered = False
        self.on_motion_cb = None
        self.on_motion_picture_cb = None
        self.should_disconnect = False

        self.picture_received = False
        self.motion_received = False

    def tearDown(self) -> None:
        self.picture_received = False
        self.motion_received = False

    def motion_subscribe(self) -> None:
        topic = f'motion/camera/{self.deviceId}'
        LOGGER.info(f'subscribe to {topic}')
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, self.on_motion)

    def motion_picture_subscribe(self) -> None:
        # <device_id>/<state>
        # state: 0 or 1
        topic = f'motion/picture/{self.deviceId}/+/+'
        LOGGER.info(f'subscribe to {topic}')
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, self.on_motion_picture)

    def _publish_people_to_trigger_motion(self) -> None:
        for i in range(self.up_threshold):
            self.client.publish(self.publishTopic, self.peopleBinary)

    def _publish_once_cat(self) -> None:
        self.client.publish(self.publishTopic, self.catBinary)

    def on_motion_picture(self, _client, _userdata, msg) -> None:
        LOGGER.info(f"on_motion_picture topic={msg.topic} expect_motion={self.expect_motion}")
        self.picture_received = True

        is_motion = int(msg.topic.split('/')[-1])
        if self.expect_motion is True:
            self.assertEqual(is_motion, 1)
        else:
            self.assertEqual(is_motion, 0)

        if self.on_motion_picture_cb:
            return self.on_motion_picture_cb()

        # if motion is already received, we can disonnect.
        if self.motion_received is True:
            LOGGER.info(f"on_motion_picture disconnect because motion received")
            self.client.disconnect()

    def on_motion(self, _client, _userdata, msg) -> None:
        payload = json.loads(msg.payload)
        LOGGER.info(f"on_motion payload={payload} should be triggered? {self.should_on_motion_triggered}")

        self.assertTrue(self.should_on_motion_triggered, "on_motion should not be triggered.")

        self.motion_received = True
        self.assertIn('status', payload)
        self.assertIn('event_ref', payload)

        if self.expect_motion is True:
            LOGGER.info(f"analyze motion")
            self.assertIn('detections', payload)

            detections = payload['detections']
            self.assertTrue(payload['status'])
            self.assertIsInstance(detections, list)
            self.assertGreater(len(detections), 0)
        else:
            LOGGER.info("analyze no motion")
            self.assertFalse(payload['status'])

        if (self.on_motion_cb):
            return self.on_motion_cb()

        # hacky things.
        # Basically, if the picture is received, we can disconnect.

        if self.expect_motion is False and self.picture_received is True:
            LOGGER.info("on_motion disconnect because expect_motion no motion and picture received.")
            self.client.disconnect()

        if self.expect_motion is True and self.picture_received is True:
            LOGGER.info("on_motion disconnect because picture was received.")
            self.client.disconnect()

    def test_motion_trigger_motion(self):
        LOGGER.info("test_motion_trigger_motion")
        self.should_on_motion_triggered = False
        print(len(self.peopleBinary))
        self.motion_subscribe()
        self.motion_picture_subscribe()

        for i in range(self.up_threshold):
            if i == self.up_threshold -1:
                self.should_on_motion_triggered = True

            LOGGER.info(f'{i} publish people')
            self.client.publish(self.publishTopic, self.peopleBinary)

        self.client.loop_forever()
        LOGGER.info("test_motion_trigger_motion ended")

    def xxtest_silly_test(self):
        LOGGER.info("silly test")
        # just to send a lot of pictures to analyze how the rpi behave.
        for i in range(1000):
            self._publish_once_cat()

        self.client.loop_forever()

    def test_no_motion_no_trigger(self):
        self.motion_subscribe()
        self.motion_picture_subscribe()
        self.should_on_motion_triggered = False

        for i in range(60):
            self._publish_once_cat()

        self.should_on_motion_triggered = True
        self._publish_people_to_trigger_motion()
        self.client.loop_forever()

    def test_motion_then_no_motion_triggers(self):
        self.motion_subscribe()
        self.motion_picture_subscribe()

        # try to publish non-people pictures, it should not answer something.
        for _ in range(10):
            self.client.publish(self.publishTopic, self.catBinary)

        def on_motion_cb():
            self.motion_received = False
            self.picture_received = False

            LOGGER.info("continue, invoke the cat!")
            self.should_on_motion_triggered = False

            for i in range(60):
                if i == 59:
                    LOGGER.info("should_on_motion_triggered=True")
                    self.on_motion_cb = None
                    self.expect_motion = False
                    self.should_on_motion_triggered = True

                    # so the next "no motion analyze" will disconnect :)
                    self.picture_received = True

                self._publish_once_cat()

        #self.on_motion_cb = on_motion_cb
        # cb on picture because it comes way later than the on_motion_cb.
        self.on_motion_picture_cb = on_motion_cb
        self.should_on_motion_triggered = True
        self.expect_motion = True
        self._publish_people_to_trigger_motion()
        self.client.loop_forever()
