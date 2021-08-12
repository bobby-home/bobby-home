import logging
import automation.tasks as automation_tasks
from devices.models import Device
from alarm.use_cases.data import InMotionCameraData
import alarm.business.in_motion as in_motion
import alarm.use_cases.out_alarm as out_alarm
from alarm.models import AlarmStatus
import alarm.notifications as alarm_notifications


LOGGER = logging.getLogger(__name__)


def camera_motion_detected(data: InMotionCameraData) -> None:
    device = Device.objects.get(device_id=data.device_id)
    saved = in_motion.save_motion(device, data.detections, data.event_ref, data.status)

    if saved is None:
        # the motion is already save in db, and so the notification should have been already send.
        return None


    if data.status is True:
        alarm_notifications.object_detected(device)
        automation_tasks.on_motion_detected.apply_async(kwargs={'device_id': device.device_id})
    else:
        alarm_notifications.object_no_more_detected(device)
        automation_tasks.on_motion_left.apply_async(kwargs={'device_id': device.device_id})

        alarm_status = AlarmStatus.objects.get(device=device)
        if alarm_status.running is False:
            LOGGER.info(f'The alarm on device {device.device_id} did not turn off because a motion was here. Not here anymore, turning off.')
            # we need to turn off the service
            out_alarm.notify_alarm_status_factory().publish_status_changed(device.pk, alarm_status)

