from datetime import timedelta
from unittest import TestCase

from django.utils import timezone
from freezegun import freeze_time

from utils.date import is_time_newer_than


class UtilsDateTestCase(TestCase):
    def setUp(self) -> None:
        pass

    @freeze_time("2020-12-21 03:21:00")
    def test_is_less_old_than(self):
        t = timezone.now() - timedelta(seconds=60)
        self.assertFalse(is_time_newer_than(t, 50))

        t = timezone.now() - timedelta(seconds=40)
        self.assertTrue(is_time_newer_than(t, 50))
