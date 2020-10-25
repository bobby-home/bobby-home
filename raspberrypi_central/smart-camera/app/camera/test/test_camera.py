import json
from unittest import TestCase
from unittest.mock import Mock, call, patch

from camera.camera import Camera
from camera.camera_analyze import Consideration
from camera.detect_motion import People, ObjectBoundingBox
from datetime import datetime, timedelta


class TestCamera(TestCase):

    def setUp(self):
        self.device_id = 'some_id'
        self.motion_topic = f'{Camera.MOTION}/{self.device_id}'
        self.picture_topic = f'{Camera.PICTURE}/{self.device_id}'

        self.box = ObjectBoundingBox(0, 0, 0, 0, [])
        self.people = People(self.box, 'class_id', 0.5)

        self.mqtt_mock = Mock()
        self.analyze_object_mock = Mock()
        self.detect_motion_mock = Mock()

        self.no_motion_payload = json.dumps({"status": False, 'event_ref': Camera.EVENT_REF_NO_MOTION})
        self.no_motion_call = call(self.motion_topic, self.no_motion_payload, retain=True, qos=1)
        self.no_motion_picture_call = call(f'{self.picture_topic}/{Camera.EVENT_REF_NO_MOTION}', [], qos=1)

        self.no_motion_calls = [self.no_motion_call, self.no_motion_picture_call]

    def _get_mqtt_client(self, client_name):
        return self.mqtt_mock

    def test_first_no_motion_process_frame(self):
        self.detect_motion_mock.process_frame.return_value = [], []
        self.analyze_object_mock.is_object_considered.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        camera.process_frame([])

        self.mqtt_mock.publish.assert_has_calls(self.no_motion_calls)

    def test_first_no_considered_motion_process_frame(self):
        """
        The system detect some motion, but this motion is not considered.
        It can be out of the ROI for instance.
        -> We have to publish "no motion".
        """
        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.is_object_considered.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        camera.process_frame([])

        self.mqtt_mock.publish.assert_has_calls(self.no_motion_calls)

    def test_first_considered_motion(self):
        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.is_object_considered.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref

        camera.process_frame([])

        self.analyze_object_mock.is_object_considered.assert_called_once()

        calls = [
            call(self.motion_topic, json.dumps({"status": True, 'event_ref': event_ref, "seen_in": {"rectangle": [1, 2]}}), retain=True, qos=1),
            call(f'{self.picture_topic}/{event_ref}', [], qos=1)
        ]
        self.mqtt_mock.publish.assert_has_calls(calls)

    def test_motion_no_more_motion(self):
        """
        - we process a frame with considerations -> the system makes 2 publishes: motion + picture.
            - we don't test publish calls, it's already done.
        - we process a frame after SECONDS_LAPSED_TO_PUBLISH secs without any considerations -> the system makes the "no more motion" call.
        """

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)
        self.analyze_object_mock.is_object_considered.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref

        camera.process_frame([])

        self.assertEqual(self.mqtt_mock.publish.call_count, 2)
        self.mqtt_mock.reset_mock()

        with patch('camera.camera.datetime') as mock_datetime:
            self.analyze_object_mock.is_object_considered.return_value = []

            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.SECONDS_LAPSED_TO_PUBLISH)
            camera.process_frame([])

            no_motion_payload = json.dumps({"status": False, 'event_ref': event_ref})
            no_motion_call = call(self.motion_topic, no_motion_payload, retain=True, qos=1)
            no_motion_picture_call = call(f'{self.picture_topic}/{event_ref}', [], qos=1)

            self.mqtt_mock.publish.assert_has_calls([no_motion_call, no_motion_picture_call])
