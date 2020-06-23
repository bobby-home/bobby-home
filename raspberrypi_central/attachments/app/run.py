from camera.camera_manager import CameraManager
from camera.camera_factory import camera_factory

cm = CameraManager(camera_factory)
cm.running = True
