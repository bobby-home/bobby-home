import dataclasses
import json
from io import BytesIO
from unittest import TestCase
from unittest.mock import Mock, call, patch

from camera.camera import Camera
from camera_analyze.camera_analyzer import Consideration
from object_detection.detect_people_utils import bounding_box_size
from object_detection.model import BoundingBox, People
from datetime import datetime, timedelta


class TestBoundingBox(TestCase):
    def test_wrong_bounding_box(self):
        with self.assertRaises(ValueError) as context:
            BoundingBox(ymin=10, ymax=5, xmin=2, xmax=5)

        with self.assertRaises(ValueError) as context:
            BoundingBox(ymin=10, ymax=15, xmin=4, xmax=2)

        # and everything should be fine here
        BoundingBox(ymin=10, ymax=15, xmin=4, xmax=20)


class TestCamera(TestCase):

    def setUp(self):
        self.device_id = 'some_id'
        self.motion_topic = f'{Camera.MOTION}/{self.device_id}'
        self.video_topic = f'{Camera.VIDEO}/{self.device_id}'
        self.picture_topic = f'{Camera.PICTURE}/{self.device_id}'

        self.bounding_box = BoundingBox(0, 0, 0, 0)
        self.bounding_box_point_and_size = bounding_box_size(self.bounding_box)
        self.people = People(self.bounding_box, 'class_id', 0.5)

        self.mqtt_mock = Mock()
        self.analyze_object_mock = Mock()
        self.detect_motion_mock = Mock()
        self.camera_recording_mock = Mock()

        self.no_motion_payload = json.dumps({"status": False, 'event_ref': Camera.EVENT_REF_NO_MOTION})
        self.no_motion_call = call(self.motion_topic, self.no_motion_payload, retain=True, qos=1)
        self.no_motion_picture_call = call(f'{self.picture_topic}/{Camera.EVENT_REF_NO_MOTION}/0', [], qos=1)

        self.no_motion_calls = [self.no_motion_call, self.no_motion_picture_call]


    def _get_mqtt_client(self, client_name):
        return self.mqtt_mock

    def test_first_no_motion_process_frame(self):
        """
        For the first frame we need to send the status even when no motion is detected.
        This is done to avoid to be locked on the status True
        Imagine: the camera detects something -> notify True
        The camera reboot for some reason -> notify False if no motion.
        """
        self.detect_motion_mock.process_frame.return_value = [], []
        self.analyze_object_mock.considered_objects.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        camera.process_frame(BytesIO())

        self.mqtt_mock.client.publish.assert_has_calls(self.no_motion_calls)


    def test_first_no_considered_motion_process_frame(self):
        """
        The system detect some motion, but this motion is not considered.
        It can be out of the ROI for instance.
        -> We have to publish "no motion".
        """
        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.considered_objects.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        camera.process_frame(BytesIO())

        self.mqtt_mock.client.publish.assert_has_calls(self.no_motion_calls)

    def test_first_considered_motion(self):
        self.bounding_box_point_and_size = bounding_box_size(self.bounding_box)

        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.considered_objects.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref

        camera.process_frame(BytesIO())

        self.analyze_object_mock.considered_objects.assert_called_once()

        payload = {
            "status": True, 'event_ref': event_ref,
            "seen_in": {
                "rectangle": {
                    'ids': [1, 2],
                    'bounding_box': dataclasses.asdict(self.bounding_box_point_and_size)
                }
            }
        }

        calls = [
            call(self.motion_topic, json.dumps(payload), retain=True, qos=1),
            call(f'{self.picture_topic}/{event_ref}/1', [], qos=1)
        ]

        self.mqtt_mock.client.publish.assert_has_calls(calls)

    def test_motion_with_all_consideration(self):
        consideration1 = Consideration(type='all')

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.considered_objects.return_value = [consideration1]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref

        camera.process_frame(BytesIO())

        self.analyze_object_mock.considered_objects.assert_called_once()

        payload = {
            "status": True, 'event_ref': event_ref,
            "seen_in": {
                "all": {
                    'ids': [None],
                    'bounding_box': dataclasses.asdict(self.bounding_box_point_and_size)
                }
            }
        }

        calls = [
            call(self.motion_topic, json.dumps(payload), retain=True, qos=1),
            call(f'{self.picture_topic}/{event_ref}/1', [], qos=1)
        ]

        self.mqtt_mock.client.publish.assert_has_calls(calls)

    def test_ping(self):
        self.detect_motion_mock.process_frame.return_value = [], []
        self.analyze_object_mock.considered_objects.return_value = []

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._initialize = False

        camera.process_frame(BytesIO())
        self.mqtt_mock.client.publish.assert_not_called()

        with patch('utils.time.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.PING_SECONDS_FREQUENCY)
            camera.process_frame(BytesIO())
            camera.process_frame(BytesIO())
            self.mqtt_mock.client.publish.assert_called_once_with(Camera.PING, qos=1)

            self.mqtt_mock.reset_mock()

            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.PING_SECONDS_FREQUENCY -1)
            camera.process_frame(BytesIO())
            self.mqtt_mock.client.publish.assert_not_called()

    def test_motion_no_more_motion(self):
        """
        - we process a frame with considerations -> the system makes 2 publishes: motion + picture.
            - we don't test publish calls, it's already done.
        - we process a frame after SECONDS_LAPSED_TO_PUBLISH secs without any considerations -> the system makes the "no more motion" call.
        """

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)
        self.analyze_object_mock.considered_objects.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref

        camera.process_frame(BytesIO())

        self.assertEqual(self.mqtt_mock.client.publish.call_count, 2)
        self.mqtt_mock.reset_mock()

        with patch('camera.camera.datetime') as mock_datetime:
            self.analyze_object_mock.considered_objects.return_value = []

            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.SECONDS_LAPSED_TO_PUBLISH_NO_MOTION)
            camera.process_frame(BytesIO())

            no_motion_payload = json.dumps({"status": False, 'event_ref': event_ref})
            no_motion_call = call(self.motion_topic, no_motion_payload, retain=True, qos=1)
            no_motion_picture_call = call(f'{self.picture_topic}/{event_ref}/0', [], qos=1)

            self.mqtt_mock.client.publish.assert_has_calls([no_motion_call, no_motion_picture_call])

    def _get_camera_for_recording_test(self):
        consideration1 = Consideration(type='all')

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.considered_objects.return_value = [consideration1]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []

        return camera, self.camera_recording_mock

    def test_start_record_video(self):
        camera, camera_recorder_mock = self._get_camera_for_recording_test()

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref
        camera.process_frame(BytesIO())
        camera.process_frame(BytesIO())
        camera_recorder_mock.start_recording.assert_called_once_with(event_ref)

        camera_recorder_mock.stop_recording.assert_not_called()
        camera_recorder_mock.split_recording.assert_called_once_with(event_ref)

    def test_split_record_video(self):
        self.detect_motion_mock.process_frame.return_value = [self.people], []
        consideration1 = Consideration(type='rectangle', id=1)
        consideration2 = Consideration(type='rectangle', id=2)
        self.analyze_object_mock.considered_objects.return_value = [consideration1, consideration2]

        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []
        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref

        camera.process_frame(BytesIO())

        video_ref = 'video_ref'
        self.camera_recording_mock.split_recording.return_value = video_ref

        self.mqtt_mock.reset_mock()
        camera.process_frame(BytesIO())

        self.camera_recording_mock.split_recording.return_value = None
        camera.process_frame(BytesIO())

        no_motion_picture_call = call(f'{self.video_topic}/{video_ref}', qos=1)
        self.mqtt_mock.client.publish.assert_has_calls([no_motion_picture_call])
