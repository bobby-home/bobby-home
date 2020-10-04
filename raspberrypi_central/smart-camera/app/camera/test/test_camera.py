from unittest import TestCase
from unittest.mock import Mock, call, patch

from camera.camera import Camera, CameraMqttTopics
from camera.camera_analyze import Consideration
from camera.detect_motion import People, ObjectBoundingBox
from datetime import datetime, timedelta


class TestCamera(TestCase):

    def setUp(self):
        self.device_id = 'some_id'
        self.motion_topic = f'{CameraMqttTopics.MOTION}/{self.device_id}'
        self.picture_topic = f'{CameraMqttTopics.PICTURE}/{self.device_id}'
        self.no_motion_payload = '{"status": false}'

        self.box = ObjectBoundingBox(0, 0, 0, 0, [])
        self.people = People(self.box, 'class_id', 0.5)

        self.mqtt_mock = Mock()
        self.analyze_object_mock = Mock()
        self.detect_motion_mock = Mock()

        self.no_motion_call = call(self.motion_topic, self.no_motion_payload, retain=True, qos=1)

    def _get_mqtt_client(self,  client_name):
        return self.mqtt_mock

    def test_first_no_motion_process_frame(self):
        self.detect_motion_mock.process_frame.return_value = [], []
        self.analyze_object_mock.is_object_considered.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera.process_frame([])

        self.mqtt_mock.publish.assert_called_once_with(self.motion_topic, self.no_motion_payload, retain=True, qos=1)

    def test_first_no_considered_motion_process_frame(self):
        """
        The system detect some motion, but this motion is not considered.
        It can be out of the ROI for instance.
        -> We have to publish "no motion".
        """
        box = ObjectBoundingBox(0, 0, 0, 0, [])
        people = People(box, 'class_id', 0.5)

        self.detect_motion_mock.process_frame.return_value = [people], []
        self.analyze_object_mock.is_object_considered.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera.process_frame([])

        self.analyze_object_mock.is_object_considered.assert_called_once()
        self.mqtt_mock.publish.assert_called_once_with(self.motion_topic, self.no_motion_payload, retain=True, qos=1)

    def test_first_considered_motion(self):
        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.is_object_considered.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera._transform_image_to_publish = lambda *a: []

        camera.process_frame([])

        self.analyze_object_mock.is_object_considered.assert_called_once()

        calls = [
            call(self.motion_topic, '{"status": true, "rectangle": [1, 2]}', retain=True, qos=1),
            call(self.picture_topic, [], qos=1)
        ]
        self.mqtt_mock.publish.assert_has_calls(calls)

    def test_motion_no_motion(self):
        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.is_object_considered.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera._transform_image_to_publish = lambda *a: []

        camera.process_frame([])

        calls = [
            call(self.motion_topic, '{"status": true, "rectangle": [1, 2]}', retain=True, qos=1),
            call(self.picture_topic, [], qos=1)
        ]

        self.mqtt_mock.publish.assert_has_calls(calls)

        self.mqtt_mock.reset_mock()
        self.analyze_object_mock.is_object_considered.return_value = []

        with patch('camera.camera.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.SECONDS_LAPSED_TO_PUBLISH)
            camera.process_frame([])

            self.mqtt_mock.publish.assert_called_once()
            self.mqtt_mock.publish.assert_has_calls([self.no_motion_call])
