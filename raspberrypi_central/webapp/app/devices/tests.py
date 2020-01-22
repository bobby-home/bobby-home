from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .models import Alert, AlertType, Attachment
from .factories import AlertTypeFactory, AlertFactory, DeviceTypeFactory, DeviceFactory, LocationFactory

class AlertModelTestCase(TestCase):

    def setUp(self):
        self.alert_type = AlertTypeFactory(type='motion')
        self.device_type = DeviceTypeFactory(type='motion')
        self.devices = []

        self.location = LocationFactory()

        for i in range(2):
            device = DeviceFactory(location=self.location, device_type=self.device_type)
            self.devices.append(device)

        self.alert = AlertFactory(devices=self.devices, alert_type=self.alert_type, severity=2)

    def test_model(self):
        pass


class AlertViewTestCase(TestCase):
    def setUp(self):
        self.alert_type = AlertTypeFactory(type='motion')
        self.device_type = DeviceTypeFactory(type='motion')
        self.devices = []

        self.location = LocationFactory()

        for i in range(2):
            device = DeviceFactory(location=self.location, device_type=self.device_type)
            self.devices.append(device)


        self.client = APIClient()

    def test_create(self):
        print('coucou')
        # 'devices': self.devices BUT throw "Object of type Device is not JSON serializable"
        # goal: alert_type: 'motion', and then perform the creation with this value.
        data = { 'severity': 'high', 'alert_type': 'motion' }

        res = self.client.post(
            reverse('alert-list'),
            data,
            format="json")

        # self.assertEqual(res.status_code, status.HTTP_200_OK)
        res.render()
        print(res.content)
        


class AttachmentViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.attachment_data = {'object_name': 'file.jpg', 'bucket_name': 'hello-world', 'storage_type': Attachment.S3}

        self.response = self.client.post(
            reverse('attachment-list'),
            self.attachment_data,
            format="json")


    def test_api_can_get_a_attachment(self):
        attachment = Attachment.objects.get()
        res = self.client.get(
            reverse('attachment-detail',
            kwargs={'pk': attachment.id}), format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertEqual(res.data, attachment)


    def test_api_can_create_attachment(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

        res = self.client.get(reverse('attachment-list'), format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertContains(res, self.attachment_data)
