from camera.detect_motion import DetectPeople, People
from camera.camera_analyze import CameraAnalyzeObject
import datetime
import struct
from PIL import Image
from image_processing.bin_image import pil_image_to_byte_array
import numpy as np
import cv2


def order_points_new(pts):
    # sort the points based on their x coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-croodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # if use Euclidean distance, it will run in error when the object
    # is trapezoid. So we should use the same simple y-coordinates order method.

    # now, sort the right-most coordinates according to their
    # y-coordinates so we can grab the top-right and bottom-right
    # points, respectively
    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


class Camera:

    def __init__(self, analyze_motion: CameraAnalyzeObject, detect_motion: DetectPeople, get_mqtt_client, device_id):
        self._analyze_motion = analyze_motion
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_motion = detect_motion
        self._start()

    def _start(self):
        self.mqtt_client = self.get_mqtt_client(client_name=f'{self._device_id}-rpi4-alarm-motion-DETECT')
        self.mqtt_client.loop_start()

    def _need_to_publish_no_motion(self) -> bool:
        if self._initialize is True:
            self._initialize = False
            return True

        time_lapsed = (self._last_time_people_detected is not None) and (
            datetime.datetime.now() - self._last_time_people_detected).seconds >= 5

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    def process_frame(self, frame):
        result, peoples, image = self.detect_motion.process_frame(frame)

        if result is True:
            peoples_in_roi = []
            for people in peoples:
                people: People
                r = self._analyze_motion.is_object_considered(frame, people.bounding_box)

                opencvImage = cv2.drawContours(frame, [people.bounding_box.contours], 0, (0,0,255), 2)

                peoples_in_roi.append(r)

            is_anybody_in_roi = any(peoples_in_roi)

            print(f'is_anybody_in_roi = {is_anybody_in_roi}, {peoples_in_roi}')

            if is_anybody_in_roi and self._last_time_people_detected is None:
                self._initialize = False
                self.mqtt_client.publish(f'motion/camera/{self._device_id}', struct.pack('?', 1), qos=1, retain=True)

                byteArr = pil_image_to_byte_array(Image.fromarray(opencvImage))

                self.mqtt_client.publish(f'motion/picture/{self._device_id}', payload=byteArr, qos=1)

            self._last_time_people_detected = datetime.datetime.now()
        elif self._need_to_publish_no_motion():
            self.mqtt_client.publish(f'motion/camera/{self._device_id}', payload=struct.pack('?', 0), qos=1, retain=True)
