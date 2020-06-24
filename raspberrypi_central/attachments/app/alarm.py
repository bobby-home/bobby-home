from mqtt.mqtt_camera import MqttCamera
from camera.camera_manager import CameraManager as CM
from camera.camera_factory import camera_factory

print('coucou')
manager = CM(camera_factory)
mqtt_camera_manager = MqttCamera(manager)
