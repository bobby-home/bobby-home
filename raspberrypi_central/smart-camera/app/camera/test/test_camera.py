from unittest import TestCase
from unittest.mock import Mock

from camera.camera import Camera


class TestCamera(TestCase):
    def test__need_to_publish_no_motion(self):
        self.fail()

    def test__publish_motion(self):
        self.fail()

    def test_process_frame(self):
        mqtt_mock = Mock()
        analyze_object_mock = Mock()
        detect_motion_mock = Mock()
        device_id = 'some id'

        detect_motion_mock.process_frame.return_value = False, [], []
        analyze_object_mock.is_object_considered.return_value = []

        def get_mqtt_client(client_name):
            return mqtt_mock

        camera = Camera(analyze_object_mock, detect_motion_mock, get_mqtt_client, device_id)
        camera.process_frame([])

        mqtt_mock.publish.assert_called_once_with('motion/camera/some id', '{"status": false}', retain=True, qos=1)
