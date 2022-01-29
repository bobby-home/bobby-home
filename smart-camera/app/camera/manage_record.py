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
        command = Command(action=split[3])

        if len(split) > 4:
            command.video_ref = split[4]

        return command

    def _on_record(self, _client, _userdata, message) -> None:
        data = self._extract_data_from_topic(message.topic)

        if data.action == Action.START.value:
            self._video_stream.start_recording(data.video_ref)
        elif data.action == Action.SPLIT.value:
            self._video_stream.split_recording(data.video_ref)
        elif data.action == Action.END.value:
            self._video_stream.stop_recording()
        else:
            LOGGER.error(f"action unkown: {data.action}")

    def _setup_listeners(self) -> None:
        self._mqtt_client.client.subscribe(f'camera/recording/{self._device_id}/#', qos=2)
        self._mqtt_client.client.message_callback_add(f'camera/recording/{self._device_id}/#', self._on_record)

def camera_record_factory(device_id: str, video_stream: PiVideoStream) -> ManageRecord:
    client = get_mqtt(f'{device_id}-manage-record')
    return ManageRecord(client, device_id, video_stream)
