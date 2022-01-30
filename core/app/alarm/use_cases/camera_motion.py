from alarm.use_cases.alarm_camera_video_manager import AlarmCameraVideoManager, alarm_camera_video_manager_factory
import logging
from alarm.integration.camera_motion import integration_camera_motion, integration_camera_no_more_motion
from alarm.integration.alarm_status import integration_alarm_status_changed
from devices.models import Device
from alarm.use_cases.data import InMotionCameraData
import alarm.business.in_motion as in_motion
from alarm.models import AlarmStatus


LOGGER = logging.getLogger(__name__)


class CameraMotion:
    def __init__(self, record_manager: AlarmCameraVideoManager) -> None:
        self._record_manager = record_manager

    def motion_detect_ended(self, data: InMotionCameraData) -> None:
        device = Device.objects.get(device_id=data.device_id)
        saved = in_motion.save_motion(device, data.detections, data.event_ref, data.status)

        # @todo will be refactored.
        if saved is None:
            # the motion is already save in db, and so the notification should have been already send.
            return None

        self._record_manager.stop_recording(device.device_id, data.event_ref)
        integration_camera_no_more_motion(device)

        alarm_status = AlarmStatus.objects.get(device=device)
        if alarm_status.running is False:
            LOGGER.info(f'The alarm on device {device.device_id} did not turn off because a motion was here. Not here anymore, turning off.')
            integration_alarm_status_changed(alarm_status)

    def motion_detected(self, data: InMotionCameraData) -> None:
        device = Device.objects.get(device_id=data.device_id)
        saved = in_motion.save_motion(device, data.detections, data.event_ref, data.status)

        # @todo will be refactored.
        if saved is None:
            # the motion is already save in db, and so the notification should have been already send.
            return None

        self._record_manager.start_recording(device.device_id, data.event_ref)
        integration_camera_motion(device)

def camera_motion_factory() -> CameraMotion:
    record_manager = alarm_camera_video_manager_factory()
    return CameraMotion(record_manager)

