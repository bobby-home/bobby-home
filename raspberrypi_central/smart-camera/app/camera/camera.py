import dataclasses
import datetime
import json
import os
import struct
import uuid
from collections import defaultdict
from io import BytesIO
from typing import List, Callable

from attr import dataclass

from camera.camera_record import CameraRecorder
from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
from loggers import LOGGER
from mqtt.mqtt_client import MqttClient
from object_detection.detect_people import DetectPeople
from object_detection.detect_people_utils import bounding_box_size
from object_detection.model import People, PeopleAllData


@dataclass
class ObjectLinkConsiderations:
    object: PeopleAllData
    considerations: List[Consideration]


class Camera:

    SERVICE_NAME = 'object_detection'
    DEVICE_ID = os.environ['DEVICE_ID']

    SECONDS_LAPSED_TO_PUBLISH_NO_MOTION = 10
    SECONDS_FIRST_MOTION_VIDEO = 10
    MOTION = 'motion/camera'
    PICTURE = 'motion/picture'
    VIDEO = 'motion/video'
    EVENT_REF_NO_MOTION = '0'

    def __init__(self, analyze_motion: CameraAnalyzer, detect_people: DetectPeople, get_mqtt: Callable[[any], MqttClient], device_id):
        self._camera_recorder = None
        self._analyze_motion = analyze_motion
        self._device_id = device_id
        self.get_mqtt = get_mqtt
        self._last_time_people_detected = None

        self._initialize = True

        self.detect_people = detect_people
        self.event_ref = self.EVENT_REF_NO_MOTION

        self.start_recording_time = None
        self.recording_first_video = False
        self._record_video_number = 0
        self.mqtt_client = None

    def start(self) -> None:
        mqtt_client = self.get_mqtt(client_name=f'{self._device_id}-{Camera.SERVICE_NAME}')
        mqtt_client.connect_keep_status(Camera.SERVICE_NAME, Camera.DEVICE_ID)
        self.mqtt_client = mqtt_client.client

    def _need_to_publish_no_motion(self) -> bool:
        if self._initialize is True:
            self._initialize = False
            return True

        time_lapsed = (self._last_time_people_detected is not None) and (
            datetime.datetime.now() - self._last_time_people_detected).seconds >= Camera.SECONDS_LAPSED_TO_PUBLISH_NO_MOTION

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    @staticmethod
    def _get_motion_payload(event_ref, object_link_considerations: List[ObjectLinkConsiderations]):
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
    def _transform_image_to_publish(image: BytesIO):
        return image.getvalue()

    @staticmethod
    def _visualize_contours(frame, considered_peoples):
        import cv2

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

    def _split_recording(self) -> None:
        LOGGER.info('split recording')
        self.recording_first_video = True
        self._publish_video_event()
        self._camera_recorder.split_recording(f'{self.event_ref}-{self._record_video_number}')

    def _publish_motion(self, payload) -> None:
        mqtt_payload = json.dumps(payload)
        LOGGER.info(f'publish motion {mqtt_payload}')

        self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)

    def _publish_video_event(self) -> None:
        self.mqtt_client.publish(f'{self.VIDEO}/{self._device_id}/{self.event_ref}-{self._record_video_number}', qos=1)
        self._record_video_number += 1

    def _publish_image(self, frame: BytesIO, is_motion: bool) -> None:
        byte_arr = self._transform_image_to_publish(frame)

        motion = '0'
        if is_motion is True:
            motion = '1'

        self.mqtt_client.publish(f'{self.PICTURE}/{self._device_id}/{self.event_ref}/{motion}', byte_arr, qos=1)

    def process_frame(self, frame: BytesIO):
        peoples, image = self.detect_people.process_frame(frame)

        considered_peoples = self._considered_peoples(peoples)
        is_any_considered_object = len(considered_peoples) > 0

        if is_any_considered_object and self._last_time_people_detected is None:
            self._initialize = False

            self.event_ref = self.generate_event_ref()

            if self._camera_recorder:
                LOGGER.info('start recording')
                self.start_recording_time = datetime.datetime.now()
                self._camera_recorder.start_recording(f'{self.event_ref}-{self._record_video_number}')

            # self._visualize_contours(frame, considered_peoples)
            payload = self._get_motion_payload(self.event_ref, considered_peoples)
            self._publish_motion(payload)
            self._publish_image(frame, is_motion=True)

        if is_any_considered_object:
            self._last_time_people_detected = datetime.datetime.now()

            time_lapsed = (self.start_recording_time is not None) and (
                datetime.datetime.now() - self.start_recording_time).seconds >= Camera.SECONDS_FIRST_MOTION_VIDEO

            if time_lapsed and self.recording_first_video is False:
                self._split_recording()

        elif self._need_to_publish_no_motion():
            payload = {
                'status': False,
                'event_ref': self.event_ref,
            }
            LOGGER.info(f'no more motion {payload}')

            if self._camera_recorder:
                LOGGER.info('stop recording')
                self._camera_recorder.stop_recording()
                self._publish_video_event()

            self.recording_first_video = False
            self.start_recording_time = None
            self._record_video_number = 0

            self._publish_motion(payload)
            self._publish_image(frame, is_motion=False)

    @staticmethod
    def generate_event_ref():
        return str(uuid.uuid4())

    @property
    def camera_recorder(self) -> CameraRecorder:
        return self._camera_recorder

    @camera_recorder.setter
    def camera_recorder(self, value: CameraRecorder):
        self._camera_recorder = value
