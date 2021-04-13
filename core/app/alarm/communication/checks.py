from django.utils import timezone
import mqtt_services.tasks as tasks


def verify_services_status(device_id: str, status: bool, is_dumb: bool) -> None:
    """When the system turns on the camera, we verify that related services are up/off. It sends tasks to check that.
    """

    kwargs = {
        'device_id': device_id,
        'service_name': 'object_detection',
        'status': status,
        'since_time': timezone.now()
    }

    if is_dumb is True and status is False:
        # @todo bugs?
        # weird case, the service object_detection does not publish off
        # for dumb cameras.
        pass
    else:
        tasks.verify_service_status.apply_async(kwargs=kwargs, countdown=15)

    kwargs_dumb = {
        'device_id': device_id,
        'service_name': 'dumb_camera',
        'status': status,
        'since_time': timezone.now()
    }

    tasks.verify_service_status.apply_async(kwargs=kwargs_dumb, countdown=15)

