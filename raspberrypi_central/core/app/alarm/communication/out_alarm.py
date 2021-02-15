from typing import Callable, Optional, List
import logging
from django.forms import model_to_dict

import alarm.business.alarm_status as alarm_status
from alarm.communication.alarm_consts import ROITypes
from alarm.messaging import alarm_messaging_factory, AlarmMessaging
from camera.models import CameraROI, CameraRectangleROI
from devices.models import Device
from utils.mqtt import MQTT
from utils.mqtt import mqtt_factory
from alarm.models import AlarmStatus


LOGGER = logging.getLogger(__name__)

class NotifyAlarmStatus:
    def __init__(self, alarm_messaging: AlarmMessaging):
        self._alarm_messaging = alarm_messaging

    def _publish(self, device: Device, status: AlarmStatus, camera_roi, rois: List[any], force=False) -> None:
        """
        The only method that actually send an mqtt message.
        It formats the mqtt payload and decide whether or not a mqtt call has to be done.
        """
        payload = None

        if status.running is True:
            payload = {
                'rois': {}
            }

            if len(rois) > 0:
                payload['rois']['definition_width'] = camera_roi.define_picture.width
                payload['rois']['definition_height'] = camera_roi.define_picture.height
                payload['rois'][ROITypes.RECTANGLES.value] = rois
            else:
                payload['rois'][ROITypes.FULL.value] = True

        if status.running is False and alarm_status.can_turn_off(device) is False and force is False:
            LOGGER.info(f'The alarm on device {device.device_id} should turn off but stay on because a motion is being detected.')
            return

        self._alarm_messaging \
            .publish_alarm_status(device.device_id, status.running, status.is_dumb, payload)


    def _publish_alarm_status_with_config(self, device: Device, status: AlarmStatus, force=False) -> None:
        camera_roi = None
        device_rois = []

        if status.running:
            try:
                device_pk = device.pk
                camera_roi = CameraROI.objects.get(device_id=device_pk)
                device_roi_querysets = list(CameraRectangleROI.actives.filter(camera_roi__device_id=device_pk))
                device_rois = [model_to_dict(device_roi) for device_roi in device_roi_querysets]
            except CameraROI.DoesNotExist:
                pass

        self._publish(device, status, camera_roi, device_rois, force)


    def publish_roi_changed(self, device_pk: int, camera_roi, rectangle_rois) -> None:
        device_status = AlarmStatus.objects.get(device_id=device_pk)

        # Of course if the service is not running the system does not need to communicate the new ROI
        # it will be done when the service will turn on.
        if device_status.running:
            self._publish(device_status.device, device_status, camera_roi, rectangle_rois)


    def publish_status_changed(self, device_pk: int, status: AlarmStatus, force=False) -> None:
        device = Device.objects.get(pk=device_pk)

        self._publish_alarm_status_with_config(device, status, force)


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
