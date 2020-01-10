from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from .models import Attachment

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
