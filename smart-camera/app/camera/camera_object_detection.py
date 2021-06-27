import numpy
import dataclasses
import datetime
import json
from utils.dict import remove_null_keys
import uuid
from io import BytesIO
from typing import List, Callable, Optional

from camera.camera_recording import CameraRecording
from loggers import LOGGER
from mqtt.mqtt_client import MqttClient
from object_detection.detect_people import DetectPeople
from object_detection.model import People
from utils.time import is_time_lapsed


@dataclasses.dataclass
class MotionPayload:
    status: bool
    event_ref: str
    detections: Optional[List[People]] = None


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (numpy.int_, numpy.intc, numpy.intp, numpy.int8,
            numpy.int16, numpy.int32, numpy.int64, numpy.uint8,
            numpy.uint16,numpy.uint32, numpy.uint64)):
            return int(obj)
        elif isinstance(obj, (numpy.float_, numpy.float16, numpy.float32, 
            numpy.float64)):
            return float(obj)
        elif isinstance(obj,(numpy.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class CameraObjectDetection:
    SERVICE_NAME = 'object_detection'

    SECONDS_LAPSED_TO_PUBLISH_NO_MOTION = 60

    MOTION = 'motion/camera'
    PICTURE = 'motion/picture'

    PING = f'ping/object_detection'
    PING_SECONDS_FREQUENCY = 60

    EVENT_REF_NO_MOTION = '0'

    def __init__(self, detect_people: DetectPeople, get_mqtt: Callable[[any], MqttClient], device_id: str, camera_recording: CameraRecording):
        self.camera_recording = camera_recording

        self._device_id = device_id
        self.get_mqtt = get_mqtt

        self._last_time_people_detected = None
        self._initialize = True

        self.detect_people = detect_people
        self.event_ref = self.EVENT_REF_NO_MOTION

        self.mqtt = None
        self.mqtt_client = None

        self.last_ping_time = None

    def start(self) -> None:
        mqtt = self.get_mqtt(client_name=f'{self._device_id}-{CameraObjectDetection.SERVICE_NAME}')
        mqtt.connect_keep_status(CameraObjectDetection.SERVICE_NAME, self._device_id)
        
        self.mqtt_client = mqtt.client
        self.mqtt = mqtt

        self.mqtt_client.loop_start()
        self.last_ping_time = datetime.datetime.now()

    def stop(self):
        self.mqtt.disconnect()
        self.mqtt_client.loop_stop()

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
            datetime.datetime.now() - self._last_time_people_detected).seconds >= CameraObjectDetection.SECONDS_LAPSED_TO_PUBLISH_NO_MOTION

        if time_lapsed:
            self._last_time_people_detected = None

        return time_lapsed

    def _publish_motion(self, payload: MotionPayload) -> None:
        dict_payload = dataclasses.asdict(payload)
        dict_payload = remove_null_keys(dict_payload)

        mqtt_payload = json.dumps(dict_payload, cls=NumpyEncoder)
        LOGGER.info(f'publish motion {mqtt_payload}')

        self.mqtt_client.publish(f'{self.MOTION}/{self._device_id}', mqtt_payload, retain=True, qos=1)

    def _publish_image(self, frame: BytesIO, is_motion: bool) -> None:
        byte_arr = self._transform_image_to_publish(frame)

        motion = '0'
        if is_motion is True:
            motion = '1'

        self.mqtt_client.publish(f'{self.PICTURE}/{self._device_id}/{self.event_ref}/{motion}', byte_arr, qos=1)

    def _publish_ping(self) -> None:
        self.mqtt_client.publish(f'{self.PING}/{self._device_id}', qos=1)

    def _start_detection(self, frame: BytesIO, considerations: List[People]) -> None:
        self._last_time_people_detected = datetime.datetime.now()
        self._initialize = False
        self.event_ref = self.generate_event_ref()

        self.camera_recording.start_recording(self.event_ref)

        payload = MotionPayload(
            status=True,
            event_ref=self.event_ref,
            detections=considerations
        )

        self._publish_motion(payload)
        self._publish_image(frame, True)

    def _detection(self) -> None:
        self._last_time_people_detected = datetime.datetime.now()

        self.camera_recording.split_recording(self.event_ref)

    def _no_more_detection(self, frame: BytesIO):
        payload = MotionPayload(
            status=False,
            event_ref=self.event_ref,
        )

        LOGGER.info(f'no more motion {payload}')
        self.camera_recording.stop_recording(self.event_ref)

        self._publish_motion(payload)
        self._publish_image(frame, False)

    def process_frame(self, frame: BytesIO) -> None:
        peoples = self.detect_people.process_frame(frame)

        is_any_considered_object = len(peoples) > 0

        # first time we detect people
        if is_any_considered_object:
            if self._last_time_people_detected is None:
                self._start_detection(frame, peoples)
            else:
                # we continue to detect people
                self._detection()
        elif self._need_to_publish_no_motion():
            # people left (some time ago), we let the core knows
            self._no_more_detection(frame)

        if is_time_lapsed(self.last_ping_time, CameraObjectDetection.PING_SECONDS_FREQUENCY, first_true=True):
            self.last_ping_time = datetime.datetime.now()
            self._publish_ping()

    @staticmethod
    def generate_event_ref() -> str:
        return str(uuid.uuid4())

