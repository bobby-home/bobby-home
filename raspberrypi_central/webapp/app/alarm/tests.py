from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from . import models


class AlarmViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create(self):
        res1 = self.client.post(
            reverse('alarmstatus-list'),
            {'running': True},
            format="json")
        
        self.assertEqual(res1.data, {'id': 1, 'running': True})

        res_get = self.client.get(reverse('alarmstatus-list'))
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(models.AlarmStatus.objects.count(), 1)
        self.assertEqual(models.AlarmStatus.objects.get().running, True)
        # self.assertEqual(res_get.data, {'id': 1, 'running': True})

        res2 = self.client.post(
            reverse('alarmstatus-list'),
            {'running': False},
            format="json")

        self.assertEqual(res2.data, {'id': 1, 'running': False})
        self.assertEqual(models.AlarmStatus.objects.count(), 1)
        self.assertEqual(models.AlarmStatus.objects.get().running, False)
