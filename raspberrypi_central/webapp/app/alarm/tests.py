from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from . import models
from api_keys.factories import ApiKeysFactory
from api_keys.models import APIKey


class AlarmViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        ApiKeysFactory()
        self.key = APIKey.objects.get(pk=1)

    def test_create(self):
        print(f'key={self.key.key}')

        res1 = self.client.post(
            reverse('alarmstatus-list'),
            {'running': True},
            format="json",
            **{'HTTP_API_KEY': self.key.key})

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res1.data, {'running': True})

        self.assertEqual(models.AlarmStatus.objects.count(), 1)
        self.assertEqual(models.AlarmStatus.objects.get().running, True)

        res_get = self.client.get(reverse('alarmstatus-list'), **{'HTTP_API_KEY': self.key.key})
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        # self.assertEqual(res_get.data, {'id': 1, 'running': True})

        res2 = self.client.post(
            reverse('alarmstatus-list'),
            {'running': False},
            format="json",
             **{'HTTP_API_KEY': self.key.key})

        self.assertEqual(res2.data, {'running': False})
        self.assertEqual(models.AlarmStatus.objects.count(), 1)
        self.assertEqual(models.AlarmStatus.objects.get().running, False)
