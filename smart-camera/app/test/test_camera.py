from typing import Optional
from camera.camera_object_detection_data import CameraObjectDetectionData
import dataclasses
import json
from io import BytesIO
from unittest import TestCase
from unittest.mock import Mock, call, patch
import uuid

from camera.camera_object_detection import CameraObjectDetection, MotionPayload
from object_detection.detect_people_utils import bounding_box_size
from object_detection.model import BoundingBox, People, People
from datetime import datetime, timedelta
from freezegun import freeze_time

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
        self.motion_topic = f'{CameraObjectDetection.MOTION}/{self.device_id}'
        self.video_topic = f'{CameraObjectDetection.VIDEO}/{self.device_id}'
        self.picture_topic = f'{CameraObjectDetection.PICTURE}/{self.device_id}'

        self.bounding_box = BoundingBox(0, 0, 0, 0)
        self.bounding_box_point_and_size = bounding_box_size(self.bounding_box)
        self.people = People(self.bounding_box, bounding_box_size(self.bounding_box), 'class_id', 0.5)

        self.mqtt_mock = Mock()
        self.detect_motion_mock = Mock()
        self.camera_recording_mock = Mock()

        self.no_motion_payload = json.dumps({"status": False, 'event_ref': CameraObjectDetection.EVENT_REF_NO_MOTION})
        self.no_motion_call = call(self.motion_topic, self.no_motion_payload, retain=True, qos=1)
        self.no_motion_picture_call = call(f'{self.picture_topic}/{CameraObjectDetection.EVENT_REF_NO_MOTION}/0', [], qos=1)

        self.no_motion_calls = [self.no_motion_call, self.no_motion_picture_call]


    def _get_mqtt_client(self, client_name):
        return self.mqtt_mock

    def _get_camera_with_mocks(self, people: bool = True, config: Optional[CameraObjectDetectionData] = None):
        self.detect_motion_mock.process_frame.return_value = [self.people] if people is True else []

        if config is None:
            self.config = CameraObjectDetectionData(deplay_to_trigger_motion=3, deplay_to_trigger_no_motion=60)
        else:
            self.config = config

        camera = CameraObjectDetection(self.detect_motion_mock, self._get_mqtt_client, self.config, self.device_id, self.camera_recording_mock)
        camera.start()
        camera._transform_image_to_publish = lambda *a: []

        self.event_ref = str(uuid.uuid4())
        camera.generate_event_ref = lambda : self.event_ref

        return camera

    def _get_payload(self, people: bool = True):
        if people is True:
            payload = MotionPayload(
                status=True,
                event_ref=self.event_ref,
                detections=[self.people]
            )
            return payload

    def _set_no_detection(self) -> None:
        self.detect_motion_mock.process_frame.return_value = []

    def _set_detection(self) -> None:
        self.detect_motion_mock.process_frame.return_value = [self.people]

    def test_first_no_motion_process_frame(self):
        """
        For the first frame we need to send the status even when no motion is detected.
        This is done to avoid to be locked on the status True
        Imagine: the camera detects something -> notify True
        The camera reboot for some reason -> notify False if no motion.
        """

        camera = self._get_camera_with_mocks(people=False)
        camera.process_frame(BytesIO())

        self.mqtt_mock.client.publish.assert_has_calls(self.no_motion_calls)


    def test_first_motion_process_frame(self):
        """
        First frame, no motion.
        -> We have to publish "no motion".
        """
        camera = self._get_camera_with_mocks(people=False)
        camera.process_frame(BytesIO())

        self.mqtt_mock.client.publish.assert_has_calls(self.no_motion_calls)

    def test_no_trigger_detection_delay(self):
        """
        When somebody is detected, it needs to be detected for X seconds
        to trigger motion. Otherwise, it should do anything.
        """
        camera = self._get_camera_with_mocks(people=True)
        camera.process_frame(BytesIO())

        self.mqtt_mock.client.publish.assert_not_called()

    def test_no_more_motion_dont_do_anything(self):
        camera = self._get_camera_with_mocks(people=False)
        camera.process_frame(BytesIO())
        # ignore the initialization.
        self.mqtt_mock.client.publish.reset_mock()

        # something is detected
        self._set_detection()
        camera.process_frame(BytesIO())

        # no more detection
        self._set_no_detection()
        self._trigger_no_more_motion(camera)

        self.mqtt_mock.client.publish.assert_not_called()

    def test_first_time_people_detected_underlying_var(self):
        """
        Test if the variable used to delay the trigger is set to None
        when nothing is detected, to reset it.
        """
        camera = self._get_camera_with_mocks(people=False)
        camera.process_frame(BytesIO())

        # something is detected
        with freeze_time("2021-10-14"):
            self._set_detection()
            camera.process_frame(BytesIO())
            self.assertIsNotNone(camera._first_time_people_detected)
            self.assertEqual(camera._first_time_people_detected, datetime(2021, 10, 14), "The variable is not set correctly.")

        # no more detection
        self._set_no_detection()
        camera.process_frame(BytesIO())

        self.assertIsNone(camera._first_time_people_detected)


    def test_start_detection(self):
        camera = self._get_camera_with_mocks(people=True)
        self._trigger_motion(camera)

        payload = MotionPayload(
            status=True,
            event_ref=self.event_ref,
            detections=[self.people]
        )

        calls = [
            call(self.motion_topic, json.dumps(dataclasses.asdict(payload)), retain=True, qos=1),
            call(f'{self.picture_topic}/{self.event_ref}/1', [], qos=1)
        ]

        self.mqtt_mock.client.publish.assert_has_calls(calls)

    def test_it_sends_ping(self):
        camera = self._get_camera_with_mocks(people=False)
        camera._initialize = False

        camera.process_frame(BytesIO())
        self.mqtt_mock.client.publish.assert_not_called()

        with patch('utils.time.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=CameraObjectDetection.PING_SECONDS_FREQUENCY)
            camera.process_frame(BytesIO())
            camera.process_frame(BytesIO())
            self.mqtt_mock.client.publish.assert_called_once_with(f'{CameraObjectDetection.PING}/{self.device_id}', qos=1)

            self.mqtt_mock.reset_mock()

            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=CameraObjectDetection.PING_SECONDS_FREQUENCY - 1)
            camera.process_frame(BytesIO())
            self.mqtt_mock.client.publish.assert_not_called()

    def _trigger_motion(self, camera) -> None:
        camera.process_frame(BytesIO())
        with patch('utils.time.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=self.config.deplay_to_trigger_motion)
            camera.process_frame(BytesIO())

    def _trigger_no_more_motion(self, camera) -> None:
        with patch('camera.camera_object_detection.datetime') as mock_datetime:
            self.detect_motion_mock.process_frame.return_value = []

            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=self.config.deplay_to_trigger_no_motion)
            camera.process_frame(BytesIO())

    def test_motion_no_more_motion(self):
        """
        - we process a frame with considerations -> the system makes 2 publishes: motion + picture.
            - we don't test publish calls, it's already done.
        - we process a frame after SECONDS_LAPSED_TO_PUBLISH secs without any considerations -> the system makes the "no more motion" call.
        """

        camera = self._get_camera_with_mocks(people=True)
        camera.process_frame(BytesIO())

        self._trigger_motion(camera)
        self._trigger_no_more_motion(camera)
        no_motion_payload = json.dumps({"status": False, 'event_ref': self.event_ref})
        no_motion_call = call(self.motion_topic, no_motion_payload, retain=True, qos=1)
        no_motion_picture_call = call(f'{self.picture_topic}/{self.event_ref}/0', [], qos=1)

        self.mqtt_mock.client.publish.assert_has_calls([no_motion_call, no_motion_picture_call])

    def test_start_record_video(self):
        camera = self._get_camera_with_mocks(people=True)

        self._trigger_motion(camera)
        self.camera_recording_mock.start_recording.assert_called_once_with(self.event_ref)
        self.camera_recording_mock.stop_recording.assert_not_called()
        # @TODO: why?
        #self.camera_recording_mock.split_recording.assert_called_once_with(self.event_ref)

    def test_split_record_video(self):
        camera = self._get_camera_with_mocks(people=True)
        camera.process_frame(BytesIO())
        video_ref = str(uuid.uuid4())

        self._trigger_motion(camera)
        camera.process_frame(BytesIO())
        self.mqtt_mock.reset_mock()

        self.camera_recording_mock.split_recording.return_value = video_ref
        camera.process_frame(BytesIO())

        self.camera_recording_mock.split_recording.return_value = None
        camera.process_frame(BytesIO())

        no_motion_picture_call = call(f'{self.video_topic}/{video_ref}', qos=1)
        self.mqtt_mock.client.publish.assert_has_calls([no_motion_picture_call])

