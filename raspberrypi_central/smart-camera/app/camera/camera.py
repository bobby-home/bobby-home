import dataclasses
import json
from collections import defaultdict
from typing import List, Callable
import paho.mqtt.client as mqtt

from attr import dataclass

from object_detection.detect_motion import DetectPeople
from object_detection.model import People
from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
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


@dataclass
class ObjectLinkConsiderations:
    object: People
    considerations: List[Consideration]


class Camera:

    SECONDS_LAPSED_TO_PUBLISH = 5
    MOTION = 'motion/camera'
    PICTURE = 'motion/picture'
    EVENT_REF_NO_MOTION = '0'

    def __init__(self, analyze_motion: CameraAnalyzer, detect_motion: DetectPeople, get_mqtt_client: Callable[[any], mqtt.Client], device_id):
        self._analyze_motion = analyze_motion
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_motion = detect_motion
        self.event_ref = self.EVENT_REF_NO_MOTION

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

    def _publish_motion(self, object_link_considerations: List[ObjectLinkConsiderations], event_ref: str) -> None:
        payload = {
            'status': True,
            'event_ref': event_ref,
            'seen_in': defaultdict(dict)
        }

        for object_link_consideration in object_link_considerations:
            object_link_consideration: ObjectLinkConsiderations

            for consideration in object_link_consideration.considerations:
                if len(payload['seen_in'][consideration.type]) == 0:
                    payload['seen_in'][consideration.type] = {'ids': []}

                payload['seen_in'][consideration.type]['ids'].append(consideration.id)
                payload['seen_in'][consideration.type]['bounding_box'] = dataclasses.asdict(object_link_consideration.object.bounding_box_point_and_size)

        mqtt_payload = json.dumps(payload)
        print(f'publish motion {mqtt_payload}')
        self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)

    def _considered_peoples(self, frame, peoples: List[People]) -> List[ObjectLinkConsiderations]:
        object_considerations: List[ObjectLinkConsiderations] = []

        for people in peoples:
            considerations = self._analyze_motion.considered_objects(frame, people.bounding_box)

            if len(considerations) > 0:
                obj = ObjectLinkConsiderations(people, considerations)
                object_considerations.append(obj)

        return object_considerations

    @staticmethod
    def _transform_image_to_publish(image):
        return pil_image_to_byte_array(Image.fromarray(image))

    def process_frame(self, frame):
        peoples, image = self.detect_motion.process_frame(frame)

        considered_peoples = self._considered_peoples(frame, peoples)
        is_any_considered_object = len(considered_peoples) > 0

        if is_any_considered_object and self._last_time_people_detected is None:
            self._initialize = False

            self.event_ref = self.generate_event_ref()
            self._publish_motion(considered_peoples, self.event_ref)

            byte_arr = self._transform_image_to_publish(frame)
            print(f'publish picture {self.event_ref}')
            self.mqtt_client.publish(f'{self.PICTURE}/{self._device_id}/{self.event_ref}/1', byte_arr, qos=1)

        if is_any_considered_object:
            self._last_time_people_detected = datetime.datetime.now()
        elif self._need_to_publish_no_motion():
            payload = {
                'status': False,
                'event_ref': self.event_ref,
            }

            print(f'no more motion {payload}')

            mqtt_payload = json.dumps(payload)
            self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)

            byte_arr = self._transform_image_to_publish(frame)
            self.mqtt_client.publish(f'{self.PICTURE}/{self._device_id}/{self.event_ref}/0', byte_arr, qos=1)

    @staticmethod
    def generate_event_ref():
        return str(uuid.uuid4())
