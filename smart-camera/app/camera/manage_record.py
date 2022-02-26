import logging
from dataclasses import dataclass
import enum
from mqtt.mqtt_client import MqttClient, get_mqtt
from camera.pivideostream import PiVideoStream

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)


class Action(enum.Enum):
    START = 'start'
    SPLIT = 'split'
    END   = 'end'

@dataclass
class Command:
    action: str
    video_ref: str
    split_number: int
    event_ref: str


class ManageRecord:
    """
    Manage record through MQTT.
    It receives MQTT messages (start/split/end), process it to manage records.
    """
    def __init__(self, mqtt_client: MqttClient, device_id: str, video_stream: PiVideoStream) -> None:
        self._video_stream = video_stream
        self._device_id = device_id
        self._mqtt_client = mqtt_client

        self._setup_listeners()
        self._mqtt_client.connect()
        self._mqtt_client.client.loop_start()

    @staticmethod
    def _extract_data_from_topic(topic: str) -> Command:
        """
        Shitty code. I'll need to improve that with regexes.
        """
        split = topic.split('/')
        if len(split) < 5:
            raise ValueError(f"topic {topic} wrong format")

        video_ref = split[4]
        video_ref_split = video_ref.split('-')
        if len(video_ref_split) == 0:
            raise ValueError(f"video_ref {video_ref} wrong format. Should be uuidv4-split_number.")

        split_number = video_ref_split[-1]
        event_ref = '-'.join(video_ref_split[:-1])

        command = Command(
            action=split[3],
            video_ref=split[4],
            split_number=int(split_number),
            event_ref=event_ref,
        )

        return command

    def _ack_video(self, video_ref: str) -> None:
        LOGGER.info(f'_ack_video video_ref={video_ref}')
        self._mqtt_client.client.publish(f'motion/video/{self._device_id}/{video_ref}', qos=1)

    def _ack_start(self, video_ref: str) -> None:
        self._mqtt_client.client.publish(f'ack/video/started/{self._device_id}/{video_ref}', qos=2)

    def _on_record(self, _client, _userdata, message) -> None:
        try:
            data = self._extract_data_from_topic(message.topic)
        except ValueError as e:
            LOGGER.error(e)
            return

        LOGGER.info(f"_on_record video_ref={data.video_ref} action={data.action} topic={message.topic}")
        action = False
        if data.action == Action.START.value:
            start = self._video_stream.start_recording(data.video_ref)
            if start is False:
                LOGGER.warn("record already started")
            else:
                self._ack_start(data.video_ref)
            return

        if data.action == Action.SPLIT.value:
            ack_video_ref = data.event_ref + f'-{data.split_number -1}'
            action = self._video_stream.split_recording(data.video_ref)
        elif data.action == Action.END.value:
            ack_video_ref = data.event_ref + f'-{data.split_number}'
            action = self._video_stream.stop_recording()
        else:
            LOGGER.error(f"action unkown: {data.action}")
            return

        if action is True:
            self._ack_video(ack_video_ref)
        else:
            LOGGER.info(f"_on_record video_ref={data.video_ref} no action to perform")

    def _setup_listeners(self) -> None:
        mqtt_topic = f'camera/recording/{self._device_id}/#'

        def subscribe(client) -> None:
            print(f'manage_record subscribe to {mqtt_topic}')
            client.subscribe(mqtt_topic, qos=1)
            client.message_callback_add(mqtt_topic, self._on_record)

        self._mqtt_client.add_on_connected_callbacks(subscribe)

def camera_record_factory(device_id: str, video_stream: PiVideoStream) -> ManageRecord:
    client = get_mqtt(f'{device_id}-manage-record')
    return ManageRecord(client, device_id, video_stream)
