from django.utils import timezone
import mqtt_services.tasks as tasks
from alarm.mqtt import MqttServices, CameraMqttServices


def verify_services_status(device_id: str, status: bool) -> None:
    """When the system turns on the camera, we verify that related services are up/off. It sends tasks to check that.
    """

    kwargs = {
        'device_id': device_id,
        'service_name': MqttServices.OBJECT_DETECTION.value,
        'status': status,
        'since_time': timezone.now()
    }

    tasks.verify_service_status.apply_async(kwargs=kwargs, countdown=15)

    kwargs_dumb = {
        'device_id': device_id,
        'service_name': CameraMqttServices.CAMERA.value,
        'status': status,
        'since_time': timezone.now()
    }

    tasks.verify_service_status.apply_async(kwargs=kwargs_dumb, countdown=15)

