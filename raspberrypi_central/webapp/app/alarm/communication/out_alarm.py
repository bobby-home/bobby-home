from typing import Callable, Optional, List

from django.forms import model_to_dict

from alarm.communication.alarm_consts import ROITypes
from alarm.messaging import alarm_messaging_factory, AlarmMessaging
from devices.models import Device
from utils.mqtt import MQTT
from utils.mqtt import mqtt_factory


class NotifyAlarmStatus:
    def __init__(self, alarm_messaging: AlarmMessaging):
        self.alarm_messaging = alarm_messaging


    def _publish(self, device_id: str, running: bool, camera_roi, rois: List[any]):
        payload = None

        if running is True:
            payload = {
                'rois': {}
            }

            if len(rois) > 0:
                payload['rois']['definition_width'] = camera_roi.define_picture.width
                payload['rois']['definition_height'] = camera_roi.define_picture.height
                payload['rois'][ROITypes.RECTANGLES.value] = rois
            else:
                payload['rois'][ROITypes.FULL.value] = True

        self.alarm_messaging \
            .publish_alarm_status(device_id, running, payload)


    def publish_roi_changed(self, device_pk: int, camera_roi, rectangle_rois):
        from alarm.models import AlarmStatus
        device_status = AlarmStatus.objects.get(device_id=device_pk)
        running = device_status.running

        if running:
            self._publish(device_status.device.device_id, running, camera_roi, rectangle_rois)


    def _publish_alarm_status_with_config(self, device: Device, running: bool):
        device_pk = device.pk

        camera_roi = None
        device_rois = []

        if running:
            from alarm.models import CameraRectangleROI, CameraROI

            try:
                camera_roi = CameraROI.objects.get(device_id=device_pk)
                device_roi_querysets = list(CameraRectangleROI.objects.filter(camera_roi__device_id=device_pk))
                device_rois = [model_to_dict(device_roi) for device_roi in device_roi_querysets]
            except CameraROI.DoesNotExist:
                pass

        self._publish(device.device_id, running, camera_roi, device_rois)


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

    mqtt_client = get_mqtt_client()
    alarm_messaging = alarm_messaging_factory(mqtt_client)

    return NotifyAlarmStatus(alarm_messaging)
