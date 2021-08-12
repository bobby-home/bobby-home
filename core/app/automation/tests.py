import struct
from unittest import mock
from django.utils import timezone
from automation.models import ActionMqttPublish, Automation
import json
from unittest.mock import ANY, call, patch
from automation.actions import Triggers
from automation.tasks import on_motion_detected, on_motion_left
from django.test import TestCase
from freezegun import freeze_time
from automation.factories import ActionMqttPublishFactory, AutomationFactory, MqttClientFactory
from devices.factories import DeviceFactory


class AutomationTestCase(TestCase):
    def setUp(self) -> None:
        self.automation = AutomationFactory(trigger_name=[Triggers.ON_MOTION_DETECTED.name, Triggers.ON_MOTION_LEFT.name])
        self.mqtt_client = MqttClientFactory()

        self.payload_json = {
            'bobby': 'is amazing!',
            'hello': 'world',
            'open_source': True
        }

        self.actions = ActionMqttPublishFactory.create_batch(
            3,
            payload_json=self.payload_json,
            automation=self.automation,
            mqtt_client=self.mqtt_client
        )
        
        self.device = DeviceFactory()
        self.device_id = self.device.device_id

    @patch('automation.actions.action_mqtt_publish.single')
    @freeze_time('2021-05-11')
    def test_last_run_datetime_update(self, _publish_mock):
        on_motion_detected(device_id=self.device_id)

        actions = ActionMqttPublish.objects.all()

        for action in actions:
            self.assertEqual(action.last_run_datetime, timezone.now())

    @patch('automation.tasks.mqtt_publish')
    def test_automation_multi_trigger(self, mqtt_publish_mock):
        actions = ActionMqttPublish.objects.all()

        on_motion_detected(device_id=self.device_id)
        on_motion_left(device_id=self.device_id)

        self.assertEqual(2, mqtt_publish_mock.call_count)

        for args in mqtt_publish_mock.call_args_list:
            #self.assertEqual(1, len(args.args))
            self.assertQuerysetEqual(args.args[0], actions, ordered=False)


    @patch('automation.actions.action_mqtt_publish.single')
    def test_mqtt_publish_json(self, publish_mock):
        on_motion_detected(device_id=self.device_id)

        calls = []
        for action in self.actions:
            mqtt_client = action.mqtt_client
            calls.append(call(
                action.topic,
                payload=json.dumps(self.payload_json),
                qos=action.qos,
                retain=action.retain,
                hostname=mqtt_client.host,
                port=mqtt_client.port,
                protocol=4,
                transport='tcp',
                auth={'username': mqtt_client.username, 'password': mqtt_client.password},
                client_id=mock.ANY
            ))
        
        publish_mock.assert_has_calls(calls)

    @patch('automation.actions.action_mqtt_publish.single')
    def test_mqtt_publish_boolean(self, publish_mock):
        ActionMqttPublish.objects.all().delete()

        ActionMqttPublishFactory.create_batch(
            2,
            payload_boolean=True,
            automation=self.automation,
            mqtt_client=self.mqtt_client
        )

        ActionMqttPublishFactory.create_batch(
            2,
            payload_boolean=False,
            automation=self.automation,
            mqtt_client=self.mqtt_client
        )

        self.actions = ActionMqttPublish.objects.all()
        
        on_motion_detected(device_id=self.device_id)

        calls = []
        for action in self.actions:
            mqtt_client = action.mqtt_client
            expected_payload = struct.pack('?', action.payload_boolean)
            calls.append(call(
                action.topic,
                payload=expected_payload,
                qos=action.qos,
                retain=action.retain,
                hostname=mqtt_client.host,
                port=mqtt_client.port,
                protocol=4,
                transport='tcp',
                auth={'username': mqtt_client.username, 'password': mqtt_client.password},
                client_id=mock.ANY
            ))
        
        publish_mock.assert_has_calls(calls)


class ActionMqttPublishTestCase(TestCase):
    def setUp(self) -> None:
        self.automation = AutomationFactory(trigger_name=[Triggers.ON_MOTION_DETECTED.name, Triggers.ON_MOTION_LEFT.name])
        self.mqtt_client = MqttClientFactory()

    @patch('automation.actions.action_mqtt_publish.single')
    def test_fstring_topic(self, publish_mock):
        device = DeviceFactory()

        action = ActionMqttPublishFactory(
            topic='test/{device.device_id}/{device.location.structure}',
            payload_boolean=True,
            automation=self.automation,
            mqtt_client=self.mqtt_client
        )

        on_motion_detected(device_id=device.device_id)
        
        mqtt_client = action.mqtt_client

        publish_mock.assert_called_once()
        args, _kwargs = publish_mock.call_args
        
        self.assertEqual(args, (f'test/{device.device_id}/{device.location.structure}',))

    @patch('automation.actions.action_mqtt_publish.single')
    def test_fstring_json(self, publish_mock):
        payload_json = {
            'device_id': '{device.device_id}',
            'location': '{device.location.structure}'
        }

        device = DeviceFactory()

        action = ActionMqttPublishFactory(
            payload_json=json.dumps(payload_json),
            automation=self.automation,
            mqtt_client=self.mqtt_client
        )

        on_motion_detected(device_id=device.device_id)
        
        mqtt_client = action.mqtt_client

        publish_mock.assert_called_once()
        _args, kwargs = publish_mock.call_args
       
        expected_payload_json = {
            'device_id': f'{device.device_id}',
            'location': f'{device.location.structure}'
        }

        self.assertEqual(kwargs.get('payload'), json.dumps(expected_payload_json))

