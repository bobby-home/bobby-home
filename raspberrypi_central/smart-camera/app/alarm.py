import os
from mqtt.mqtt_status_manage_thread import MqttStatusManageThread
from thread.thread_manager import ThreadManager
from camera.camera_factory import camera_factory
from camera.play_sound import PlaySound
from mqtt.mqtt_client import get_mqtt_client
from camera.videostream import VideoStream


mqtt_client = get_mqtt_client(f"{os.environ['DEVICE_ID']}-rpi4-alarm-motion")

MQTT_ALARM_CAMERA_TOPIC = 'status/alarm'


def run():
    camera = camera_factory(get_mqtt_client)

    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    # TODO: see issue #78
    VideoStream(camera.processFrame, resolution=(
        CAMERA_WIDTH, CAMERA_HEIGHT), framerate=1, usePiCamera=False)


manager = ThreadManager(run)
MqttStatusManageThread(mqtt_client, manager, MQTT_ALARM_CAMERA_TOPIC)


def run_sound():
    PlaySound()


sound_manager = ThreadManager(run_sound)
MqttStatusManageThread(mqtt_client, sound_manager, 'status/sound')

mqtt_client.loop_forever()
