from unittest import mock
from django.utils import timezone
from automation.models import ActionMqttPublish
import json
from unittest.mock import ANY, call, patch
from automation.actions import Triggers
from automation.tasks import on_motion_detected
from django.test import TestCase
from freezegun import freeze_time
from automation.factories import ActionMqttPublishFactory, AutomationFactory, MqttClientFactory


# Create your tests here.
class AutomationTestCase(TestCase):
    def setUp(self) -> None:
        self.automation = AutomationFactory(trigger_name=Triggers.ON_MOTION_DETECTED.name)
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

    @patch('automation.actions.action_mqtt_publish.single')
    @freeze_time('2021-05-11')
    def test_last_run_datetime_update(self, _publish_mock):
        on_motion_detected(data={})

        actions = ActionMqttPublish.objects.all()

        for action in actions:
            self.assertEqual(action.last_run_datetime, timezone.now())


    @patch('automation.actions.action_mqtt_publish.single')
    def test_mqtt_publish(self, publish_mock):
        on_motion_detected(data={})

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
