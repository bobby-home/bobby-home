import logging
from alarm.use_cases.data import InMotionCameraData 
import alarm.business.in_motion as in_motion
import alarm.use_cases.out_alarm as out_alarm
from alarm.use_cases.play_sound import play_sound
from alarm.models import AlarmStatus
import alarm.notifications as alarm_notifications

LOGGER = logging.getLogger(__name__)

"""
Class with methods to react to camera motion events.
Each method is executed in a corresponding Celery Task even if it's totally transparent here (and have to stay transparent!).
"""

def camera_motion_detected(data: InMotionCameraData) -> None:
    device, motion = in_motion.save_motion(data.device_id, data.seen_in, data.event_ref, data.status)

    if device is None:
        # the motion is already save in db, and so the notification should have been already send.
        return None


    if data.status is True:
        alarm_notifications.object_detected(device)
    else:
        alarm_notifications.object_no_more_detected(device)
        
        alarm_status = AlarmStatus.objects.get(device=device)
        if alarm_status.running is False:
            LOGGER.info(f'The alarm on device {device.device_id} did not turn off because a motion was here. Not here anymore, turning off.')
            # we need to turn off the service
            out_alarm.notify_alarm_status_factory().publish_status_changed(device.pk, alarm_status)

    play_sound(data.device_id, data.status)

