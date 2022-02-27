import alarm.notifications as alarm_notifications
from devices.models import Device
import automation.tasks as automation_tasks


def integration_camera_motion(device: Device, event_ref: str) -> None:
    from alarm.tasks import camera_recording_split_video
    alarm_notifications.object_detected(device)
    automation_tasks.on_motion_detected.apply_async(kwargs={'device_id': device.device_id})
    # 30s
    camera_recording_split_video.apply_async(args=[event_ref], countdown=30)

def integration_camera_no_more_motion(device: Device) -> None:
    alarm_notifications.object_no_more_detected(device)
    automation_tasks.on_motion_left.apply_async(kwargs={'device_id': device.device_id})
