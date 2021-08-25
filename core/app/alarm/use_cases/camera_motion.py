import logging
from alarm.integration.camera_motion import integration_camera_motion, integration_camera_no_more_motion
from alarm.integration.alarm_status import integration_alarm_status_changed
from devices.models import Device
from alarm.use_cases.data import InMotionCameraData
import alarm.business.in_motion as in_motion
from alarm.models import AlarmStatus


LOGGER = logging.getLogger(__name__)


def camera_motion_detected(data: InMotionCameraData) -> None:
    device = Device.objects.get(device_id=data.device_id)
    saved = in_motion.save_motion(device, data.detections, data.event_ref, data.status)

    if saved is None:
        # the motion is already save in db, and so the notification should have been already send.
        return None

    if data.status is True:
        integration_camera_motion(device)
    else:
        integration_camera_no_more_motion(device)

        alarm_status = AlarmStatus.objects.get(device=device)
        if alarm_status.running is False:
            LOGGER.info(f'The alarm on device {device.device_id} did not turn off because a motion was here. Not here anymore, turning off.')
            # we need to synchronize services.
            integration_alarm_status_changed(alarm_status)
