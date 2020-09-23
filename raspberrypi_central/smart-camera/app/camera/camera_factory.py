from .camera import Camera
import os
from camera.detect_motion import DetectPeople
from camera.camera_roi import ROICamera, RectangleROI

rectangle_roi = RectangleROI(1,1,1,1)
camera_roi = ROICamera(rectangle_roi)


def camera_factory(get_mqtt_client) -> Camera:
    return Camera(camera_roi, DetectPeople(), get_mqtt_client, os.environ['DEVICE_ID'])
