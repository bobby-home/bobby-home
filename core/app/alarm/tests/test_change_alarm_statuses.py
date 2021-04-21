from devices.models import Device
import uuid

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from alarm.use_cases.alarm_status import AlarmScheduleChangeStatus, AlarmChangeStatus
from alarm.factories import AlarmScheduleFactory, AlarmStatusFactory
from alarm.models import AlarmSchedule, AlarmStatus, Ping
from camera.models import CameraMotionDetected
from devices.factories import DeviceFactory
from house.factories import HouseFactory


class ChangeStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()
        self.device1 = DeviceFactory()
        self.device2 = DeviceFactory()

        self.devices = [self.device1, self.device2]

        self.running_alarm_statuses = [
            AlarmStatusFactory(running=True, device=self.device1),
            AlarmStatusFactory(running=True, device=self.device2)
        ]

        for status in self.running_alarm_statuses:
            Ping.objects.create(
                device_id=status.device.device_id,
                service_name='object_detection',
                consecutive_failures=2,
                last_update=timezone.now()
            )

    def _reset_pings(self, device_ids = None):
        pings = Ping.objects.filter(service_name='object_detection')
        
        if device_ids is None:
            devices = Device.objects.all()
            device_ids = [device.device_id for device in devices]
        
        for ping in pings:
            if ping.device_id in device_ids:
                self.assertEqual(ping.consecutive_failures, 0)
            else:
                self.assertEqual(ping.consecutive_failures, 2)
            

    def test_reset_pings(self):
        AlarmChangeStatus().all_change_status(False)
        self._reset_pings()

    def test_schedule(self):
        schedule: AlarmSchedule = AlarmScheduleFactory()
        
        device = DeviceFactory()
        another_status = AlarmStatusFactory(running=False, device=device)
        
        Ping.objects.create(
            device_id=device.device_id,
            service_name='object_detection',
            consecutive_failures=2,
            last_update=timezone.now()
        )

        
        for status in self.running_alarm_statuses:
            schedule.alarm_statuses.add(status)

        change_status = AlarmScheduleChangeStatus()
        change_status.turn_off(schedule.uuid)
        
        device_ids = [device.device_id for device in self.devices]
        self._reset_pings(device_ids)


class AlarmChangeStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()

        self.running_alarm_statuses = [
            AlarmStatusFactory(running=True),
            AlarmStatusFactory(running=True)
        ]

        super().setUp()

    def test_all(self):
        AlarmChangeStatus().all_change_status(False)
        statuses = AlarmStatus.objects.filter(running=False)
        self.assertEqual(2, len(statuses))

    def test_reverse(self):
        AlarmChangeStatus().reverse_status(alarm_status_pk=self.running_alarm_statuses[0].pk)
        false_running = AlarmStatus.objects.get(pk=self.running_alarm_statuses[0].pk)
        true_running = AlarmStatus.objects.get(pk=self.running_alarm_statuses[1].pk)

        self.assertFalse(false_running.running)
        self.assertTrue(true_running.running)


class AlarmScheduleChangeStatusTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.house = HouseFactory()

        self.running_alarm_statuses = [
            AlarmStatusFactory(running=True),
            AlarmStatusFactory(running=True)
        ]

        self.schedule: AlarmSchedule = AlarmScheduleFactory()

        for status in self.running_alarm_statuses:
            self.schedule.alarm_statuses.add(status)

    def test_set_alarm_status(self):
        change_status = AlarmScheduleChangeStatus()
        change_status.turn_off(self.schedule.uuid)
        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertFalse(cur_alarm_status.running)

        change_status.turn_on(self.schedule.uuid)
        cur_alarm_statuses = AlarmStatus.objects.all()

        for cur_alarm_status in cur_alarm_statuses:
            self.assertTrue(cur_alarm_status.running)

    def test_turn_off_motion_being(self):
        """
        Even if a motion is being detected, we change the database status.
        Its on the use_cases side that changes: don't tell to the service to actually turn off.
        """
        event_ref = str(uuid.uuid4())

        CameraMotionDetected.objects.create(event_ref=event_ref, motion_started_at=timezone.now(), device=self.running_alarm_statuses[0].device)

        change_status = AlarmScheduleChangeStatus()

        change_status.turn_off(self.schedule.uuid)

        alarm_statuses = AlarmStatus.objects.all()
        self.assertTrue(len(alarm_statuses), 2)

        self.assertFalse(alarm_statuses[0].running)
        self.assertFalse(alarm_statuses[1].running)

