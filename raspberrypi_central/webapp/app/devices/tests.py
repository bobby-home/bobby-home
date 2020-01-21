from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .models import Alert, AlertType, Attachment
from .factories import AlertTypeFactory, AlertFactory, DeviceTypeFactory, DeviceFactory, LocationFactory

class ModelTestCase(TestCase):

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


# class ViewTestCase(TestCase):

#     def setUp(self):
#         self.client = APIClient()

#         self.attachment_data = {'object_name': 'file.jpg', 'bucket_name': 'hello-world', 'storage_type': Attachment.S3}
#         self.response = self.client.post(
#             reverse('create'),
#             self.attachment_data,
#             format="json")


#     def test_api_can_create_attachment(self):
#         self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
