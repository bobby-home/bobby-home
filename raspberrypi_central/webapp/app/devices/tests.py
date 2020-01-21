from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .models import Alert, AlertType, Attachment
from .factories import AlertTypeFactory, AlertFactory, DeviceFactory, LocationFactory

class ModelTestCase(TestCase):

    def setUp(self):
        self.alert_type = AlertTypeFactory()
        self.devices = []

        location = LocationFactory()

        for i in range(2):
            device = DeviceFactory(location=location)
            self.devices.append(device)

        self.alert = AlertFactory(devices=self.devices, alert_type=self.alert_type, severity=2)

    def test_model(self):
        pass


class ViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.attachment_data = {'object_name': 'file.jpg', 'bucket_name': 'hello-world', 'storage_type': Attachment.S3}
        self.response = self.client.post(
            reverse('create'),
            self.attachment_data,
            format="json")


    def test_api_can_create_attachment(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
