import logging
from dataclasses import dataclass
import enum
from mqtt.mqtt_client import MqttClient, get_mqtt
from camera.pivideostream import PiVideoStream


LOGGER = logging.getLogger(__name__)


class Action(enum.Enum):
    START = 'start'
    SPLIT = 'split'
    END   = 'end'

@dataclass
class Command:
    action: str
    video_ref: str = ""


class ManageRecord:
    """
    Manage record through MQTT.
    It receives MQTT messages (start/split/end), process it to manage records.
    """
    def __init__(self, mqtt_client: MqttClient, device_id: str, video_stream: PiVideoStream) -> None:
        self._video_stream = video_stream
        self._device_id = device_id
        self._mqtt_client = mqtt_client

        self._mqtt_client.connect()
        self._mqtt_client.client.loop_start()

        self._setup_listeners()

    @staticmethod
    def _extract_data_from_topic(topic: str) -> Command:
        split = topic.split('/')
        if len(split) < 5:
            raise ValueError(f"topic {topic} wrong format")
        command = Command(action=split[3], video_ref=split[4])

        return command

    def _ack_video(self, video_ref: str) -> None:
        self._mqtt_client.client.publish(f'motion/video/{self._device_id}/{video_ref}', qos=1)

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
                LOGGER.info("record already started")
        elif data.action == Action.SPLIT.value:
            action = self._video_stream.split_recording(data.video_ref)
        elif data.action == Action.END.value:
            action = self._video_stream.stop_recording()
        else:
            LOGGER.error(f"action unkown: {data.action}")
            return

        if action is True:
            LOGGER.info(f"_on_record video_ref={data.video_ref} ack_video")
            self._ack_video(data.video_ref)
        else:
            LOGGER.info(f"_on_record video_ref={data.video_ref} no action to perform")

    def _setup_listeners(self) -> None:
        mqtt_topic = f'camera/recording/{self._device_id}/#'

        def subscribe(client) -> None:
            client.subscribe(mqtt_topic, qos=1)
            client.message_callback_add(mqtt_topic, self._on_record)

        self._mqtt_client.add_on_connected_callbacks(subscribe)

def camera_record_factory(device_id: str, video_stream: PiVideoStream) -> ManageRecord:
    client = get_mqtt(f'{device_id}-manage-record')
    return ManageRecord(client, device_id, video_stream)
