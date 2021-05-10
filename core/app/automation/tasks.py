from typing import Dict
from automation.models import Automation
from celery import shared_task

from automation.actions.action_mqtt_publish import mqtt_publish
from automation.actions import Triggers


@shared_task()
def on_motion_detected(data: Dict) -> None:
    
    automations = Automation.objects.filter(trigger_name=Triggers.ON_MOTION_DETECTED.value)

    for automation in automations:
        actions = automation.actions_mqtt_publish.all()
        mqtt_publish(actions)        
