import uuid

from django.utils import timezone
from django.db import models
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from alarm.business.alarm_schedule import get_next_off_schedule, get_next_on_schedule, get_device_next_off_schedule, \
    get_device_next_on_schedule
from devices.models import Device
from django.db import transaction
from django.urls import reverse


class Ping(models.Model):
    device_id = models.CharField(max_length=8)
    service_name = models.CharField(max_length=100)

    # it's possible that a service never sent any ping.
    last_update = models.DateTimeField(default=None, blank=True, null=True)

    consecutive_failures = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)

    class Meta:
        unique_together = ['device_id', 'service_name']

    def __str__(self):
        return f'Service {self.service_name} on device {self.device_id} last ping at {self.last_update}'

class AlarmStatusManager(models.Manager):
    def with_device_and_location(self):
        return self.select_related('device', 'device__location')

class AlarmStatus(models.Model):
    class Meta:
        verbose_name = 'alarm status'
        verbose_name_plural = 'alarm statuses'

    objects = AlarmStatusManager()

    running = models.BooleanField(
        help_text='Either or not the alarm is running on the device. If it runs, it monitor the device camera to react if a danger is recognized.',
        default=False
    )

    device = models.OneToOneField(
        Device, on_delete=models.CASCADE,
        help_text="The device that is controlled by the alarm. If you do not find the desired device, it means that an alarm is already linked to it."
    )

    is_dumb = models.BooleanField(
        default=True,
        help_text='Either or not the device is dumb, which means it runs the dumb camera software. Typically used for low-end devices such as RaspberryPi zero, esp...'
    )

    def __str__(self):
        return f'Status is {self.running} for {self.device}'

    def get_next_off_schedule(self):
        return get_device_next_off_schedule(timezone.now(), self.device.pk)

    def get_next_on_schedule(self):
        return get_device_next_on_schedule(timezone.now(), self.device.pk)

    def get_absolute_url(self):
        return reverse('alarm:status-detail', args=[str(self.id)])


class AlarmScheduleManager(models.Manager):
    # @TODO: could be useless to have this method here.
    def get_next_off(self):
        return get_next_off_schedule(timezone.now(), self)

    # @TODO: could be useless to have this method here.
    def get_next_on(self):
        return get_next_on_schedule(timezone.now(), self)


class AlarmScheduleDateRange(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    turn_on_task = models.OneToOneField(
            PeriodicTask,
            editable=False,
            blank=True,
            null=True,
            on_delete=models.PROTECT,
            related_name='alarm_schedule_date_range_on')

    turn_off_task = models.OneToOneField(
            PeriodicTask,
            editable=False,
            blank=True,
            null=True,
            on_delete=models.PROTECT,
            related_name='alarm_schedule_date_range_off')


class AlarmSchedule(models.Model):
    objects = AlarmScheduleManager()

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    start_time = models.TimeField(
        help_text='When the alarm should start to monitor if a danger is recognized to react.'
    )
    end_time = models.TimeField(
        help_text='When the alarm should stop the monitoring and thus it will not react to anything.'
    )

    monday    = models.BooleanField()
    tuesday   = models.BooleanField()
    wednesday = models.BooleanField()
    thursday  = models.BooleanField()
    friday    = models.BooleanField()
    saturday  = models.BooleanField()
    sunday    = models.BooleanField()

    turn_on_task = models.OneToOneField(
        PeriodicTask,
        editable=False,
        on_delete=models.PROTECT,
        related_name='alarm_schedule_on'
    )

    turn_off_task = models.OneToOneField(
        PeriodicTask,
        editable=False,
        on_delete=models.PROTECT,
        related_name='alarm_schedule_off'
    )

    alarm_statuses = models.ManyToManyField(
        AlarmStatus,
        related_name='alarm_schedules',
        help_text='List of alarm statuses to impact.'
    )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)

            if self.turn_off_task:
                self.turn_off_task.delete()

            if self.turn_on_task:
                self.turn_on_task.delete()

    def get_absolute_url(self):
        return reverse('alarm:schedule-detail', args=[str(self.id)])
