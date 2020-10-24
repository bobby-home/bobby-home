import json
from collections import defaultdict
from typing import List
from enum import Enum
from camera.detect_motion import DetectPeople, People
from camera.camera_analyze import CameraAnalyzeObject, Consideration
import datetime
from PIL import Image
from image_processing.bin_image import pil_image_to_byte_array
import numpy as np
import uuid


def order_points_new(pts):
    # sort the points based on their x-coordinates
    x_sorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-croodinate points
    left_most = x_sorted[:2, :]
    right_most = x_sorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    left_most = left_most[np.argsort(left_most[:, 1]), :]
    (tl, bl) = left_most

    # if use Euclidean distance, it will run in error when the object
    # is trapezoid. So we should use the same simple y-coordinates order method.

    # now, sort the right-most coordinates according to their
    # y-coordinates so we can grab the top-right and bottom-right
    # points, respectively
    right_most = right_most[np.argsort(right_most[:, 1]), :]
    (tr, br) = right_most

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


class Camera:

    SECONDS_LAPSED_TO_PUBLISH = 5
    MOTION = 'motion/camera'
    PICTURE = 'motion/picture'

    def __init__(self, analyze_motion: CameraAnalyzeObject, detect_motion: DetectPeople, get_mqtt_client, device_id):
        self._analyze_motion = analyze_motion
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_motion = detect_motion

    def start(self):
        self.mqtt_client = self.get_mqtt_client(client_name=f'{self._device_id}-rpi4-alarm-motion-DETECT')
        self.mqtt_client.loop_start()

    def _need_to_publish_no_motion(self) -> bool:
        if self._initialize is True:
            self._initialize = False
            return True

        time_lapsed = (self._last_time_people_detected is not None) and (
            datetime.datetime.now() - self._last_time_people_detected).seconds >= Camera.SECONDS_LAPSED_TO_PUBLISH

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    def _publish_motion(self, considerations: List[Consideration], event_ref: str) -> None:
        payload = {
            'status': True,
            'event_ref': event_ref,
            'seen_in': defaultdict(list)
        }

        for consideration in considerations:
            payload['seen_in'][consideration.type].append(consideration.id)

        mqtt_payload = json.dumps(payload)
        print(f'publish motion {mqtt_payload}')
        self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)

    def _considered_peoples(self, frame, peoples: List[People]):
        peoples_in_roi = []
        for people in peoples:
            considerations = self._analyze_motion.is_object_considered(frame, people.bounding_box)
            # frame = cv2.drawContours(frame, [people.bounding_box.contours], 0, (0, 0, 255), 2)
            peoples_in_roi.extend(considerations)

        return peoples_in_roi

    @staticmethod
    def _transform_image_to_publish(image):
        return pil_image_to_byte_array(Image.fromarray(image))

    def process_frame(self, frame):
        peoples, image = self.detect_motion.process_frame(frame)
        peoples_in_roi = self._considered_peoples(frame, peoples)

        is_anybody_in_roi = len(peoples_in_roi) > 0
        print(f'is_anybody_in_roi={is_anybody_in_roi}')

        if is_anybody_in_roi and self._last_time_people_detected is None:
            self._initialize = False

            event_ref = str(uuid.uuid4())
            self._publish_motion(peoples_in_roi, event_ref)

            byte_arr = self._transform_image_to_publish(frame)
            print(f'publish picture {event_ref}')
            self.mqtt_client.publish(f'{self.PICTURE}/{self._device_id}/{event_ref}', byte_arr, qos=1)

        if is_anybody_in_roi:
            self._last_time_people_detected = datetime.datetime.now()
        elif self._need_to_publish_no_motion():
            payload = {
                'status': False
            }

            mqtt_payload = json.dumps(payload)
            self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)
