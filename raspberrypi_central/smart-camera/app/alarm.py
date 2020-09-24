import os
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from thread.thread_manager import ThreadManager
from camera.camera_factory import camera_factory
from camera.play_sound import PlaySound
from mqtt.mqtt_client import get_mqtt_client
from camera.videostream import VideoStream


device_id = os.environ['DEVICE_ID']

mqtt_client = get_mqtt_client(f"{device_id}-rpi4-alarm-motion")


def run(*args, **kwargs):
    print(f'from mqtt: {args} {kwargs}')
    camera = camera_factory(get_mqtt_client)

    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    # TODO: see issue #78
    VideoStream(camera.process_frame, resolution=(
        CAMERA_WIDTH, CAMERA_HEIGHT), framerate=1, usePiCamera=False)


manager = ThreadManager(run)
mqtt_status_manage_thread_factory(device_id, 'camera', mqtt_client, manager)


def run_sound():
    PlaySound()


sound_manager = ThreadManager(run_sound)
mqtt_status_manage_thread_factory(device_id, 'speaker', mqtt_client, sound_manager)

mqtt_client.loop_forever()
