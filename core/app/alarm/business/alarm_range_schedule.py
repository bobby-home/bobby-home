from django.db.models import Q
from django.utils import timezone
from alarm.models import AlarmScheduleDateRange
from typing import Optional


def get_current_range_schedule() -> Optional[AlarmScheduleDateRange]:
    now = timezone.now()
    
    try:
        return AlarmScheduleDateRange.objects.get(
                Q(datetime_start__lte=now),
                Q(datetime_end__gt=now) | Q(datetime_end__isnull=True)
        )
    except AlarmScheduleDateRange.DoesNotExist:
        return None

