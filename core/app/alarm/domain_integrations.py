from typing import List
import automation.tasks as automation_tasks
from alarm.models import AlarmStatus


def on_motion(status: bool) -> None:
    if status is True:
        automation_tasks.on_motion_detected.apply_async()
    else:
        automation_tasks.on_motion_left.apply_async()


def alarm_status_changed(alarm_statuses: List[AlarmStatus]):
    pass
