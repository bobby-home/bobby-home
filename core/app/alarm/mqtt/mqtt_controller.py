from distutils.util import strtobool
from alarm.models import AlarmStatus
from devices.models import Device
from alarm.use_cases.alarm_status import AlarmChangeStatus
import dataclasses
from dataclasses import dataclass, field
import re
import os
from typing import Optional, Sequence, Type, TypeVar 

from hello_django.loggers import LOGGER
from utils.mqtt.mqtt_data import MqttTopicFilterSubscription, MqttTopicSubscription, \
    MqttMessage, MqttTopicSubscriptionBoolean, MqttTopicSubscriptionJson
from utils.mqtt import MQTT
import alarm.tasks as tasks
from alarm.business.alarm_ping import register_ping
import hello_django.settings as settings
from alarm.use_cases.data import Detection, InMotionCameraData, InMotionPictureData, InMotionVideoData


CAMERA_TOPIC_MATCHER = r"^(?P<type>[\w]+)/(?P<service>[\w]+)/(?P<device_id>[\w]+)"

# uuid v4 regex, source: https://stackoverflow.com/a/38191078/6555414
PICTURE_EVENT_REF_GROUP = r"(?i)(?P<event_ref>[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}|[0])"
VIDEO_EVENT_REF_GROUP = r"(?i)(?P<event_ref>[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12})-(?P<video_split_number>[0-9]+)"


@dataclass
class CameraTopic:
    type: str
    service: str
    device_id: str

@dataclass
class CameraMotionPicturePayload:
    image: bytearray


@dataclass
class CameraMotionPictureTopic(CameraTopic):
    event_ref: str
    status: str
    bool_status: bool = field(init=False)
    filename: str = field(init=False)

    _topic_matcher = CAMERA_TOPIC_MATCHER + rf"/{PICTURE_EVENT_REF_GROUP}/(?P<status>[0-1])$" 

    def __post_init__(self):
        self.bool_status = self.status == '1'
        self.filename = f'{self.event_ref}-{self.status}.jpg'


@dataclass
class CameraMotionVideoPayload:
    pass


@dataclass
class CameraMotionVideoTopic(CameraTopic):
    video_ref: str = field(init=False)
    event_ref: str
    video_split_number: int
    _topic_matcher = CAMERA_TOPIC_MATCHER + rf"/{VIDEO_EVENT_REF_GROUP}$"

    def __post_init__(self):
        # data is extracted from regex.groupdict and it does not give int type but str.
        self.video_split_number = int(self.video_split_number)

        self.video_ref = f'{self.event_ref}-{self.video_split_number}'


@dataclass
class CameraMotionPayload:
    event_ref: str
    status: bool
    detections: Sequence[Detection]


UPDATE_STATUS_MATCHER = r"^(?P<service>[\w]+)/(?P<device_id>[\w]+)"

@dataclass
class UpdateStatusTopic:
    service: str
    device_id: Optional[str] = None

    _topic_matcher = UPDATE_STATUS_MATCHER


@dataclass
class CameraMotionTopic(CameraTopic):
    _topic_matcher = CAMERA_TOPIC_MATCHER

T = TypeVar('T', Type[CameraMotionPictureTopic], Type[CameraMotionVideoTopic], Type[CameraMotionTopic], Type[UpdateStatusTopic])

def topic_regex(topic: str, t: T) -> Optional[T]:
    match = re.match(t._topic_matcher, topic) 

    if match:
        groups = match.groupdict()
        return t(**groups) # type: ignore
    
    raise ValueError(f'topic {topic} wrong format. {t._topic_matcher}')


def on_motion_camera(message: MqttMessage) -> None:
    topic = topic_regex(message.topic, CameraMotionTopic)
    payload = message.payload

    LOGGER.info(f'on_motion_camera payload={payload} topic={topic}')

    detections_plain = payload.get('detections', [])
    payload['detections'] = [Detection(**d) for d in detections_plain]

    data_payload = CameraMotionPayload(**payload)

    in_data = InMotionCameraData(
        device_id=topic.device_id,
        event_ref=data_payload.event_ref,
        status=data_payload.status,
        detections=data_payload.detections,
    )

    if in_data.event_ref != '0':
        # 0 = initialization
        tasks.camera_motion_detected.apply_async(args=[dataclasses.asdict(in_data)])


def on_motion_video(message: MqttMessage) -> None:
    topic = topic_regex(message.topic, CameraMotionVideoTopic)
    LOGGER.info(f'on_motion_video: topic={topic} {message.topic}')

    in_data = InMotionVideoData(
        device_id=topic.device_id,
        event_ref=topic.event_ref,
        video_ref=topic.video_ref,
        video_split_number=topic.video_split_number
    )

    # The system has some latency to save the video,
    # so we add a little countdown so the video will more likely be available after x seconds.
    tasks.camera_motion_video.apply_async(args=[dataclasses.asdict(in_data)], countdown=3)


def on_motion_picture(message: MqttMessage):
    topic = topic_regex(message.topic, CameraMotionPictureTopic)
    LOGGER.info(f'on_motion_picture topic={topic}')

    if topic.event_ref == "0":
        # Initialization: no motion
        return

    data_payload = CameraMotionPicturePayload(image=message.payload)

    """
    Warning: hacky thing.
    - We need to save the file here because we cannot send it to a Task (memory consumption!).
    - So we save manually the file to the disk at the right place for Django.
    - But we can't use model.file.save('name.jpg', content, True) because we do not have the model instance here this is the task job.
    - So we go with low-level API.
    - at the end, picture_path is an absolute path e.g: "/usr/src/app/media/1be409e1-7625-490a-9a8a-428ba4b8e88c.jpg"
    """

    picture_path = os.path.join(settings.MEDIA_ROOT, topic.filename)


    """
    edge case: I should not explicitly raise this error because
    open() should do, but it was not in production.
    See issue #186 for further information.
    """
    if os.path.isfile(picture_path):
        raise FileExistsError()

    with open(picture_path, 'wb') as f:
        f.write(data_payload.image)

    in_data = InMotionPictureData(
        device_id=topic.device_id,
        picture_path=picture_path,
        event_ref=topic.event_ref,
        status=topic.bool_status
    )

    tasks.camera_motion_picture.apply_async(args=[dataclasses.asdict(in_data)])


@dataclass
class PingData:
    device_id: str
    service_name: str

def on_ping_data_from_topic(topic: str) -> PingData:
    data = topic.split('/')
    return PingData(data[2], data[1])


def on_ping(message: MqttMessage) -> None:
    data = on_ping_data_from_topic(message.topic)
    register_ping(data.device_id, data.service_name)


def register(mqtt: MQTT):
    mqtt.add_subscribe((
        MqttTopicFilterSubscription(
            topic='update/status/+/+',
            qos=1,
            topics=[
                MqttTopicSubscriptionBoolean('update/status/+/+', on_update_status),
            ]
        ),
        MqttTopicFilterSubscription(
            topic='motion/#',
            qos=1,
            topics=[
                MqttTopicSubscriptionJson('motion/camera/+', on_motion_camera),
                MqttTopicSubscription('motion/picture/+/+/+', on_motion_picture),
                MqttTopicSubscription('motion/video/+/+', on_motion_video),
            ],
        ),
        MqttTopicFilterSubscription(
           # ping/{service_name}/{device_id}
            topic='ping/+/+',
            qos=1,
            topics=[
                MqttTopicSubscription('ping/+/+', on_ping)
            ]
        ),
    ))

