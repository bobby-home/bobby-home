from .camera import Camera

def camera_factory(mqtt_client) -> Camera:
    return Camera(mqtt_client)
