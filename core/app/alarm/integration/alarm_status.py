from alarm.use_cases.out_alarm import notify_alarm_status_factory
from alarm.models import AlarmStatus
import automation.tasks as automation_tasks


def integration_alarm_status_changed(alarm_status: AlarmStatus) -> None:
    automation_tasks.on_alarm_status_changed.apply_async(kwargs={
        'device_id': alarm_status.device.device_id,
        'status': alarm_status.running
    })

    notify_alarm_status_factory().publish_status_changed(alarm_status.device.pk, alarm_status)
