from django.utils import timezone
from alarm.models import AlarmScheduleDateRange
from typing import Optional


def get_current_range_schedule() -> Optional[AlarmScheduleDateRange]:
    now = timezone.now()
    
    try:
        return AlarmScheduleDateRange.objects.get(datetime_start__lte=now, datetime_end__gt=now)
    except AlarmScheduleDateRange.DoesNotExist:
        return None

