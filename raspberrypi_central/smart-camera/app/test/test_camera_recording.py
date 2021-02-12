from unittest import TestCase
from unittest.mock import Mock, patch

from camera.camera import Camera
from camera_analyze.camera_analyzer import Consideration
from datetime import datetime, timedelta

from object_detection.detect_people_utils import bounding_box_size
from object_detection.model import BoundingBox, People


class TestCameraRecording(TestCase):
    def setUp(self) -> None:
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


    def _get_camera_for_recording_test(self):
        consideration1 = Consideration(type='all')

        self.detect_motion_mock.process_frame.return_value = [self.people], []
        self.analyze_object_mock.considered_objects.return_value = [consideration1]

        camera_recorder_mock = Mock()
        camera = Camera(self.analyze_object_mock, self.detect_motion_mock, self._get_mqtt_client, self.device_id, self.camera_recording_mock)
        camera.camera_recorder = camera_recorder_mock
        camera.start()
        camera._transform_image_to_publish = lambda *a: []

        return camera, camera_recorder_mock

    def test_start_record_video(self):
        camera, camera_recorder_mock = self._get_camera_for_recording_test()

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref
        camera.process_frame([])
        camera.process_frame([])
        camera_recorder_mock.start_recording.assert_called_once_with(f'{event_ref}-0')
        camera_recorder_mock.stop_recording.assert_not_called()
        camera_recorder_mock.split_recording.assert_not_called()

    def test_split_record_video(self):
        camera, camera_recorder_mock = self._get_camera_for_recording_test()

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref
        camera.process_frame([])
        camera_recorder_mock.start_recording.assert_called_once_with(f'{event_ref}-0')

        with patch('camera.camera.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.SECONDS_FIRST_MOTION_VIDEO)

            self.mqtt_mock.reset_mock()
            camera.process_frame([])
            camera.process_frame([])

            camera_recorder_mock.split_recording.assert_called_once_with(f'{event_ref}-1')
            camera_recorder_mock.start_recording.assert_called_once_with(f'{event_ref}-0')
            camera_recorder_mock.stop_recording.assert_not_called()

            no_motion_picture_call = call(f'{self.video_topic}/{event_ref}-0', qos=1)
            self.mqtt_mock.publish.assert_has_calls([no_motion_picture_call])

    def test_stop_record_video(self):
        camera, camera_recorder_mock = self._get_camera_for_recording_test()

        event_ref = 'event_ref'
        camera.generate_event_ref = lambda : event_ref
        camera.process_frame([])
        camera_recorder_mock.start_recording.assert_called_once_with(f'{event_ref}-0')

        with patch('camera.camera.datetime') as mock_datetime:
            self.mqtt_mock.reset_mock()
            self.detect_motion_mock.process_frame.return_value = [], []
            self.analyze_object_mock.considered_objects.return_value = []
            mock_datetime.datetime.now.return_value = datetime.now() + timedelta(seconds=Camera.SECONDS_LAPSED_TO_PUBLISH_NO_MOTION)

            camera._split_recording()
            camera.process_frame([])
            camera_recorder_mock.stop_recording.assert_called_once_with()

            no_motion_payload = json.dumps({"status": False, 'event_ref': event_ref})
            no_motion_call = call(self.motion_topic, no_motion_payload, retain=True, qos=1)

            split_video_call = call(f'{self.video_topic}/{event_ref}-0', qos=1)
            video_call = call(f'{self.video_topic}/{event_ref}-1', qos=1)
            self.mqtt_mock.publish.assert_has_calls([split_video_call, video_call, no_motion_call])
