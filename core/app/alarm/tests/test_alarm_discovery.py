from devices.factories import DeviceFactory
import json
from unittest.mock import Mock, patch
from alarm.models import AlarmStatus
from alarm.use_cases.data import DiscoverAlarmData
from devices.models import Device, DeviceType
from django.test.testcases import TestCase
from alarm.use_cases.alarm_discovery import discover_alarm
import alarm.tasks as alarm_tasks


class AlarmDiscoveryTaskTestCase(TestCase):
    
    @patch("alarm.use_cases.alarm_discovery.discover_alarm")
    def test_it_calls_use_case(self, discover_alarm_patch):
        payload = {
                "type": "esp32cam",
                "id": "some_id",
        }

        data = DiscoverAlarmData(**payload)

        alarm_tasks.discover_alarm(payload)
        discover_alarm_patch.assert_called_once_with(data)


class AlarmDiscoveryTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_it_creates_device_with_device_type(self):
        in_data = DiscoverAlarmData('some_id', 'esp32cam')
        discover_alarm(in_data)

        devices = Device.objects.all()
        self.assertEqual(1, len(devices))
        
        device = devices[0]

        self.assertEqual(device.device_type.type, 'esp32cam')

    def test_it_creates_one_type(self):
        in_data = DiscoverAlarmData('some_id', 'esp32cam')
        discover_alarm(in_data)
        discover_alarm(in_data)
        discover_alarm(in_data)

        devices = Device.objects.all()
        self.assertEqual(3, len(devices))
        
        device_types = DeviceType.objects.all()
        self.assertEqual(1, len(device_types))

    def test_it_creates_alarm_status(self):
        in_data = DiscoverAlarmData('some_id', 'esp32cam')
        discover_alarm(in_data)
        discover_alarm(in_data)

        alarm_statuses = AlarmStatus.objects.all()
        self.assertEqual(2, len(alarm_statuses))
        
        for alarm_status in alarm_statuses:
            self.assertEqual(alarm_status.device.device_type.type, 'esp32cam')

    def test_it_creates_alarm_status_for_given_device(self):
        device = DeviceFactory()
        device_id = device.device_id

        in_data = DiscoverAlarmData(id='some_id', device_id=device_id)
        discover_alarm(in_data)

        devices = Device.objects.all()
        self.assertEqual(1, len(devices))

        types = DeviceType.objects.all()
        self.assertEqual(1, len(types))

        alarm_statuses = AlarmStatus.objects.all()
        self.assertEqual(1, len(alarm_statuses))
        alarm_status = alarm_statuses[0]

        self.assertEqual(alarm_status.device.device_id, device_id)

    @patch('alarm.use_cases.alarm_discovery.mqtt_factory')
    def test_it_sends_mqtt_answer(self, mqtt_factory_patch):
        mqtt_mock = Mock()
        mqtt_factory_patch.return_value = mqtt_mock

        in_data = DiscoverAlarmData('some_id', 'esp32cam')
        discover_alarm(in_data)

        devices = Device.objects.all()
        device = devices[0]

        mqtt_factory_patch.assert_called_once()

        payload = {
            "device_id": device.device_id,
            "id": "some_id",
        }  

        mqtt_mock.publish.assert_called_once_with("registered/alarm", json.dumps(payload))
