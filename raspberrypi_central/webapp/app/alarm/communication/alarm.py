from typing import Callable

from django.forms import model_to_dict

from alarm.messaging import alarm_messaging_factory
from utils.mqtt import MQTT


class NotifyAlarmStatus:
    def __init__(self, get_mqtt_client: Callable[[], MQTT]):
        self._mqtt_client = get_mqtt_client()

    def publish(self, device_id: str, running: bool = None):
        if running is None:
            from alarm.models import AlarmStatus
            device_status = AlarmStatus.objects.get(device=device_id)
            running = device_status.running

        device_roi_obj = None

        if running:
            from alarm.models import CameraRectangleROI

            # values() gives us python dictionaries, but they're in a QuerySet which is not JSON serializable
            # so we put everything in a python list which is JSON serializable.
            device_roi = list(CameraRectangleROI.objects.filter(device=device_id).values())

            device_roi_obj = device_roi

        alarm_messaging_factory(self._mqtt_client) \
            .publish_alarm_status(device_id, running, device_roi_obj)
