from typing import Callable, Optional, List
import logging
from django.forms import model_to_dict

import alarm.business.alarm_status as alarm_status
from alarm.use_cases import checks
from alarm.messaging import alarm_messaging_factory, AlarmMessaging
from devices.models import Device
from utils.mqtt import MQTT
from utils.mqtt import mqtt_factory
from alarm.models import AlarmStatus


class NotifyAlarmStatus:
    """Class to coordinate the communication with alarm services.
    Methods to call when you need to communicate with an alarm.
    """
    def __init__(self, alarm_messaging: AlarmMessaging):
        self._alarm_messaging = alarm_messaging

    def _publish(self, device: Device, status: AlarmStatus) -> None:
        """
        The only method that actually send an mqtt message.
        It formats the mqtt payload and decide whether or not a mqtt call has to be done.
        """
        payload = {}

        checks.verify_services_status(device.device_id, status.running)

        self._alarm_messaging \
            .publish_alarm_status(device.device_id, status.running, payload)

    def _publish_alarm_status_with_config(self, device: Device, status: AlarmStatus) -> None:
        self._publish(device, status)

    def publish_status_changed(self, device_pk: int, status: AlarmStatus) -> None:
        device = Device.objects.get(pk=device_pk)

        self._publish_alarm_status_with_config(device, status)

    def publish_device_connected(self, device_id: str) -> None:
        """When an alarm device connects, send everything it needs to run."""
        device_status = AlarmStatus.objects.get(device__device_id=device_id)
        device = device_status.device

        self._publish_alarm_status_with_config(device, device_status)


def notify_alarm_status_factory(get_mqtt_client: Optional[Callable[[], MQTT]] = None) -> NotifyAlarmStatus:
    if get_mqtt_client is None:
        get_mqtt_client = mqtt_factory

    mqtt_client = get_mqtt_client()
    alarm_messaging = alarm_messaging_factory(mqtt_client)

    return NotifyAlarmStatus(alarm_messaging)
