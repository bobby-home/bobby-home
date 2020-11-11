from typing import Callable, Optional

from django.forms import model_to_dict

from alarm.messaging import alarm_messaging_factory
from devices.models import Device
from utils.mqtt import MQTT
from utils.mqtt import mqtt_factory


class NotifyAlarmStatus:
    def __init__(self, alarm_messaging, get_mqtt_client: Callable[[], MQTT]):
        mqtt_client = get_mqtt_client()
        self.alarm_messaging = alarm_messaging(mqtt_client)

    def publish_roi_changed(self, device_pk: int, rectangle_rois):
        from alarm.models import AlarmStatus
        device_status = AlarmStatus.objects.get(device_id=device_pk)
        running = device_status.running

        if running:
            self.alarm_messaging \
                .publish_alarm_status(device_status.device.device_id, running, rectangle_rois)

    def _publish_alarm_status_with_config(self, device: Device, running: bool):
        device_pk = device.pk
        device_rois = None

        if running:
            from alarm.models import CameraRectangleROI

            device_roi_querysets = list(CameraRectangleROI.objects.filter(camera_roi__device_id=device_pk))
            device_rois = [model_to_dict(device_roi) for device_roi in device_roi_querysets]

        self.alarm_messaging.publish_alarm_status(device.device_id, running, device_rois)

    def publish_status_changed(self, device_pk: int, running: bool):
        device = Device.objects.get(pk=device_pk)
        self._publish_alarm_status_with_config(device, running)

    def publish_device_connected(self, device_id: str):
        from alarm.models import AlarmStatus
        device_status = AlarmStatus.objects.get(device__device_id=device_id)
        device = device_status.device

        self._publish_alarm_status_with_config(device, device_status.running)

def notify_alarm_status_factory(get_mqtt_client: Optional[Callable[[], MQTT]] = None):
    if get_mqtt_client is None:
        get_mqtt_client = mqtt_factory

    return NotifyAlarmStatus(alarm_messaging_factory, get_mqtt_client)
