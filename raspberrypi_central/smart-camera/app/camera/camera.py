import dataclasses
import json
from collections import defaultdict
from typing import List, Callable

import cv2
import paho.mqtt.client as mqtt

from attr import dataclass

from object_detection.detect_people import DetectPeople
from object_detection.detect_people_utils import bounding_box_size
from object_detection.model import People, PeopleAllData
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
    object: PeopleAllData
    considerations: List[Consideration]


class Camera:

    SECONDS_LAPSED_TO_PUBLISH = 5
    MOTION = 'motion/camera'
    PICTURE = 'motion/picture'
    EVENT_REF_NO_MOTION = '0'

    def __init__(self, analyze_motion: CameraAnalyzer, detect_people: DetectPeople, get_mqtt_client: Callable[[any], mqtt.Client], device_id):
        self._analyze_motion = analyze_motion
        self._device_id = device_id
        self.get_mqtt_client = get_mqtt_client
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_people = detect_people
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

    @staticmethod
    def _publish_motion_payload(event_ref, object_link_considerations):
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
                payload['seen_in'][consideration.type]['bounding_box'] = dataclasses.asdict(
                    object_link_consideration.object.bounding_box_point_and_size)

        return payload


    def _publish_motion(self, object_link_considerations: List[ObjectLinkConsiderations], event_ref: str) -> None:
        payload = self._publish_motion_payload(event_ref, object_link_considerations)

        mqtt_payload = json.dumps(payload)
        print(f'publish motion {mqtt_payload}')
        self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)


    def _considered_peoples(self, peoples: List[People]) -> List[ObjectLinkConsiderations]:
        object_considerations: List[ObjectLinkConsiderations] = []

        for people in peoples:
            considerations = self._analyze_motion.considered_objects(people.bounding_box)

            if len(considerations) > 0:
                people = PeopleAllData(**dataclasses.asdict(people), bounding_box_point_and_size=bounding_box_size(people.bounding_box))
                obj = ObjectLinkConsiderations(people, considerations)
                object_considerations.append(obj)

        return object_considerations

    @staticmethod
    def _transform_image_to_publish(image):
        return pil_image_to_byte_array(Image.fromarray(image))

    @staticmethod
    def _visualize_contours(frame, considered_peoples):
        """
        This method is here to debug and develop the system.
        We draw considered_peoples contours thanks to OpenCV to the frame.
        Why is it useful only for debugging purposes? Because this feature is done on the fly by the main system.
        We want to send the "raw" picture without any transformation and the bounding boxes data to visualize things if the user wants it.
        Otherwise we would impact badly the picture with unnecessary fixed drawing.
        """
        for object_link_consideration in considered_peoples:
            object_link_consideration: ObjectLinkConsiderations
            frame = cv2.drawContours(frame, [object_link_consideration.object.bounding_box.contours], 0, (0, 0, 255), 2)

        return frame

    def process_frame(self, frame):
        peoples, image = self.detect_people.process_frame(frame)

        considered_peoples = self._considered_peoples(peoples)
        is_any_considered_object = len(considered_peoples) > 0

        if is_any_considered_object and self._last_time_people_detected is None:
            self._initialize = False

            self.event_ref = self.generate_event_ref()
            self._publish_motion(considered_peoples, self.event_ref)

            # self._visualize_contours(frame, considered_peoples)

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
