from mqtt.mqtt_camera import MqttCamera
from motion.camera_manager import CameraManager as CM
from motion.camera_factory import camera_factory

print('coucou')
manager = CM(camera_factory)
mqtt_camera_manager = MqttCamera(manager)
