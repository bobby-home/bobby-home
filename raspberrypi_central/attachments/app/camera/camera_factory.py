from .camera import Camera

def camera_factory(get_mqtt_client) -> Camera:
    return Camera(get_mqtt_client)
