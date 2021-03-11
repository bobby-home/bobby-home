from django.db import models


class MqttServicesConnectionStatusLogs(models.Model):
    class Meta:
        get_latest_by = 'created_at'

    device_id = models.CharField(max_length=8)
    service_name = models.CharField(max_length=100)
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.service_name} switched {self.status} on device {self.device_id} at {self.created_at}'
