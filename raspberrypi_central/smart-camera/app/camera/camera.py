import dataclasses
import datetime
import json
import uuid
from collections import defaultdict
from io import BytesIO
from typing import List, Callable

from camera.camera_recording import CameraRecording
from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
from loggers import LOGGER
from mqtt.mqtt_client import MqttClient
from object_detection.detect_people import DetectPeople
from object_detection.detect_people_utils import bounding_box_size
from object_detection.model import People, PeopleAllData
from utils.time import is_time_lapsed


@dataclasses.dataclass
class ObjectLinkConsiderations:
    object: PeopleAllData
    considerations: List[Consideration]


class Camera:
    SERVICE_NAME = 'object_detection'

    SECONDS_LAPSED_TO_PUBLISH_NO_MOTION = 60

    MOTION = 'motion/camera'
    PICTURE = 'motion/picture'
    VIDEO = 'motion/video'

    PING = f'ping/object_detection'
    PING_SECONDS_FREQUENCY = 60

    EVENT_REF_NO_MOTION = '0'

    def __init__(self, analyze_motion: CameraAnalyzer, detect_people: DetectPeople, get_mqtt: Callable[[any], MqttClient], device_id: str, camera_recording: CameraRecording):
        self.camera_recording = camera_recording

        self._analyze_motion = analyze_motion
        self._device_id = device_id
        self.get_mqtt = get_mqtt

        self._last_time_people_detected = None
        self._initialize = True

        self.detect_people = detect_people
        self.event_ref = self.EVENT_REF_NO_MOTION

        self.mqtt_client = None

        self.last_ping_time = None

    def start(self) -> None:
        mqtt_client = self.get_mqtt(client_name=f'{self._device_id}-{Camera.SERVICE_NAME}')
        mqtt_client.connect_keep_status(Camera.SERVICE_NAME, self._device_id)
        self.mqtt_client = mqtt_client.client

        self.mqtt_client.loop_start()
        self.last_ping_time = datetime.datetime.now()

    def __del__(self):
        self.mqtt_client.loop_stop()

    @staticmethod
    def _get_motion_payload(event_ref: str, object_link_considerations: List[ObjectLinkConsiderations]):
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

    def _need_to_publish_no_motion(self) -> bool:
        """

        Returns
        -------
        bool
            Whether or not it needs to publish "no motion" event.
        """
        if self._initialize is True:
            self._initialize = False
            return True

        time_lapsed = (self._last_time_people_detected is not None) and (
            datetime.datetime.now() - self._last_time_people_detected).seconds >= Camera.SECONDS_LAPSED_TO_PUBLISH_NO_MOTION

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    def _publish_motion(self, payload) -> None:
        mqtt_payload = json.dumps(payload)
        LOGGER.info(f'publish motion {mqtt_payload}')

        self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)

    def _publish_video_event(self, video_ref: str) -> None:
        LOGGER.info(f'publish video {video_ref}')
        self.mqtt_client.publish(f'{self.VIDEO}/{self._device_id}/{video_ref}', qos=1)

    def _publish_image(self, frame: BytesIO, is_motion: bool) -> None:
        byte_arr = self._transform_image_to_publish(frame)

        motion = '0'
        if is_motion is True:
            motion = '1'

        self.mqtt_client.publish(f'{self.PICTURE}/{self._device_id}/{self.event_ref}/{motion}', byte_arr, qos=1)

    def _publish_ping(self) -> None:
        self.mqtt_client.publish(f'{self.PING}/{self._device_id}', qos=1)

    def _start_detection(self, frame: BytesIO, considerations: List[ObjectLinkConsiderations]) -> None:
        self._last_time_people_detected = datetime.datetime.now()
        self._initialize = False
        self.event_ref = self.generate_event_ref()

        LOGGER.info('start recording')
        self.camera_recording.start_recording(self.event_ref)

        payload = self._get_motion_payload(self.event_ref, considerations)
        self._publish_motion(payload)
        self._publish_image(frame, True)

    def _detection(self) -> None:
        self._last_time_people_detected = datetime.datetime.now()

        video_ref = self.camera_recording.split_recording(self.event_ref)

        if isinstance(video_ref, str):
            self._publish_video_event(video_ref)

    def _no_more_detection(self, frame: BytesIO):
        payload = {
            'status': False,
            'event_ref': self.event_ref,
        }

        LOGGER.info(f'no more motion {payload}')

        LOGGER.info('stop recording')
        video_ref = self.camera_recording.stop_recording(self.event_ref)

        if isinstance(video_ref, str):
            self._publish_video_event(video_ref)

        self._publish_motion(payload)
        self._publish_image(frame, False)

    def process_frame(self, frame: BytesIO) -> None:
        peoples, image = self.detect_people.process_frame(frame)

        considered_peoples = self._considered_peoples(peoples)
        is_any_considered_object = len(considered_peoples) > 0

        # first time we detect people
        if is_any_considered_object:
            if self._last_time_people_detected is None:
                self._start_detection(frame, considered_peoples)
            else:
                # we continue to detect people
                self._detection()
        elif self._need_to_publish_no_motion():
            # people left (some time ago), we let the core knows
            self._no_more_detection(frame)

        if is_time_lapsed(self.last_ping_time, Camera.PING_SECONDS_FREQUENCY, first_true=True):
            self.last_ping_time = datetime.datetime.now()
            self._publish_ping()

    @staticmethod
    def generate_event_ref():
        return str(uuid.uuid4())

    @property
    def analyze_motion(self):
        return self._analyze_motion

    @analyze_motion.setter
    def analyze_motion(self, analyzer: CameraAnalyzer):
        self._analyze_motion = analyzer
