from typing import Callable, Optional, List

from django.forms import model_to_dict

from alarm.communication.alarm_consts import ROITypes
from alarm.messaging import alarm_messaging_factory, AlarmMessaging
from camera.models import CameraROI, CameraRectangleROI, CameraMotionDetected
from devices.models import Device
from utils.mqtt import MQTT
from utils.mqtt import mqtt_factory
from alarm.models import AlarmStatus


class NotifyAlarmStatus:
    def __init__(self, alarm_messaging: AlarmMessaging):
        self.alarm_messaging = alarm_messaging

    def _can_turn_off(self, device: Device) -> bool:
        try:
            motion = CameraMotionDetected.objects.filter(device=device, closed_by_system=False).latest('motion_started_at')
        except CameraMotionDetected.DoesNotExist:
            return True

        return motion.motion_ended_at is not None

    def _publish(self, device: Device, running: bool, camera_roi, rois: List[any]):
        """
        The only method that actually send an mqtt message.
        It formats the mqtt payload and decide whether or not a mqtt call has to be done.
        """
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

        if running is False and self._can_turn_off(device) is False:
            return

        self.alarm_messaging \
            .publish_alarm_status(device.device_id, running, payload)


    def publish_roi_changed(self, device_pk: int, camera_roi, rectangle_rois):
        device_status = AlarmStatus.objects.get(device_id=device_pk)
        running = device_status.running

        if running:
            self._publish(device_status.device, running, camera_roi, rectangle_rois)


    def _publish_alarm_status_with_config(self, device: Device, running: bool):

        camera_roi = None
        device_rois = []

        if running:
            try:
                device_pk = device.pk
                camera_roi = CameraROI.objects.get(device_id=device_pk)
                device_roi_querysets = list(CameraRectangleROI.actives.filter(camera_roi__device_id=device_pk))
                device_rois = [model_to_dict(device_roi) for device_roi in device_roi_querysets]
            except CameraROI.DoesNotExist:
                pass

        self._publish(device, running, camera_roi, device_rois)


    def publish_status_changed(self, device_pk: int, running: bool):
        device = Device.objects.get(pk=device_pk)

        self._publish_alarm_status_with_config(device, running)


    def publish_device_connected(self, device_id: str):
        """When an alarm device connects, send everything it needs to run."""
        device_status = AlarmStatus.objects.get(device__device_id=device_id)
        device = device_status.device

        self._publish_alarm_status_with_config(device, device_status.running)


def notify_alarm_status_factory(get_mqtt_client: Optional[Callable[[], MQTT]] = None):
    if get_mqtt_client is None:
        get_mqtt_client = mqtt_factory

    mqtt_client = get_mqtt_client()
    alarm_messaging = alarm_messaging_factory(mqtt_client)

    return NotifyAlarmStatus(alarm_messaging)
