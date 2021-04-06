import uuid
from unittest import TestCase

from camera.camera_producer_consumer import FrameProducer
from unittest.mock import Mock
import multiprocessing as mp

from camera.camera_record import MPCameraRecorder


class TestFrameProducer(TestCase):
    def setUp(self) -> None:
        pass

    def test_split_record(self):
        camera_record_event = mp.Event()
        camera_record_queue = mp.Queue()
        camera_mock = Mock()

        video_ref = str(uuid.uuid4())

        recorder = MPCameraRecorder(camera_record_event, camera_record_queue)
        producer = FrameProducer([], camera_record_event, camera_record_queue)
        producer.set_camera_steam(camera_mock)

        recorder.start_recording(video_ref)
        self.assertTrue(camera_record_event.is_set())
        self.assertEqual(camera_record_queue.qsize(), 1)

        producer._manage_record()

        camera_mock.start_recording.assert_called_once_with(video_ref)
        camera_mock.split_recording.assert_not_called()

        camera_mock.reset_mock()

        video_ref = str(uuid.uuid4())
        video_ref = f'{MPCameraRecorder.SPLIT_RECORDING_TASK}/{video_ref}'
        recorder.split_recording(video_ref)
        producer._manage_record()

        # do for /event_ref with split video
        camera_mock.split_recording.assert_called_once_with(video_ref)
        camera_mock.start_recording.assert_not_called()
