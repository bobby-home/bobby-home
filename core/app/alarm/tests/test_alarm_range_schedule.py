from django.utils import timezone
from alarm.models import AlarmScheduleDateRange
from alarm.business.alarm_range_schedule import get_current_range_schedule
from django.test import TestCase

class AlarmRangeScheduleBusinessTestCase(TestCase):
    def test_get_current_range_schedule_now(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now(),
           datetime_end=timezone.now() + timezone.timedelta(hours=5)
        )

        g = get_current_range_schedule()
        self.assertIsNotNone(g)

    def test_get_current_range_schedule_past(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() - timezone.timedelta(hours=1),
           datetime_end=timezone.now() + timezone.timedelta(hours=5)
        )

        g = get_current_range_schedule()
        self.assertIsNotNone(g)

    def test_get_current_range_schedule_not_found(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() + timezone.timedelta(hours=1),
           datetime_end=timezone.now() + timezone.timedelta(hours=5)
        )

        self.assertIsNone(get_current_range_schedule())

        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() - timezone.timedelta(hours=2),
           datetime_end=timezone.now() - timezone.timedelta(hours=1)
        )

        self.assertIsNone(get_current_range_schedule())

    def test_get_current_range_schedule_no_end(self):
        AlarmScheduleDateRange.objects.create(
           datetime_start=timezone.now() - timezone.timedelta(hours=1),
        )

        g = get_current_range_schedule()
        self.assertIsNotNone(g)

